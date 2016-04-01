#! /usr/bin/env python3
"""
Update a GitHub repository with data from The Counted provided by the Guardian.
"""
import csv
import difflib
import io
import os
import zipfile

import github3
import requests


SOURCE_URL = "https://interactive.guim.co.uk/2015/the-counted/thecounted-data.zip"
GITHUB_USER = "flother"
GITHUB_REPO = "thecounted"
GITHUB_BRANCH = "master"
USER_AGENT = "The Counted repo (+https://github.com/{}/{})".format(GITHUB_USER,
                                                                   GITHUB_REPO)


class CountedZipFile(zipfile.ZipFile):

    """
    Sub-class of Python's zipfile.ZipFile class that's specialised at handling
    the ZIP archive of the bulk download of The Counted data provided by the
    Guardian newspaper.
    """

    def files(self):
        """Yield a CountedData object for each file in the ZIP archive."""
        try:
            self._files
        except AttributeError:
            self._files = tuple(CountedData(self, info)
                                for info in self.infolist())
        for file_ in self._files:
            if file_.is_data_file():
                file_.parse()
            yield file_

    def is_dirty(self):
        """
        Returns True if any of the files in the ZIP archive are new, or if any
        of the files' content is different from that committed on GitHub.
        """
        return any((f.is_dirty() for f in self.files()))

    def _ids(self, record_type):
        record_ids = []
        for file_ in self.files():
            if file_.is_data_file():
                for r in getattr(file_, record_type + "_ids")():
                    record_ids.append(r)
        return record_ids

    def new_ids(self):
        """
        Return a list of unique ids, one for each row that's been added to any
        data file in the ZIP archive since the last commit.
        """
        return self._ids("new")

    def modified_ids(self):
        """
        Return a list of unique ids, one for each row that's been modified in
        any data file in the ZIP archive since the last commit.
        """
        return self._ids("modified")

    def deleted_ids(self):
        """
        Return a list of unique ids, one for each row that's been removed from
        any data file in the ZIP archive since the last commit.
        """
        return self._ids("deleted")

    def _names(self, record_type):
        record_names = []
        for file_ in self.files():
            if file_.is_data_file():
                if file_.is_data_file() and file_._parsed is not True:
                    file_.parse()
                for r in getattr(file_, record_type + "_names")():
                    record_names.append(r)
        return record_names

    def new_names(self):
        """
        Return a list of names, one for each person that's been added to any
        data file in the ZIP archive since the last commit.
        """
        return self._names("new")

    def modified_names(self):
        """
        Return a list of names, one for each person that's been modified in any
        data file in the ZIP archive since the last commit.
        """
        return self._names("modified")

    def deleted_names(self):
        """
        Return a list of names, one for each person that's been removed from
        any data file in the ZIP archive since the last commit.
        """
        return self._names("deleted")


class CountedData(object):

    """A file within the Guardian's ZIP archive."""

    def __init__(self, zip_file, zip_info):
        self.zip_file = zip_file
        self.zip_info = zip_info
        self._parsed = False

    def is_data_file(self):
        """
        Returns True if the file's name ends with ``.csv`` (case-insensitive),
        False otherwise.
        """
        return os.path.splitext(self.zip_info.filename)[1].lower() == ".csv"

    def is_new_file(self):
        """
        Returns True if this file isn't yet in the GitHub repo, False
        otherwise.
        """
        return requests.head(self.github_url()).status_code == 404

    def is_dirty(self):
        """
        Returns True if the file is new to the ZIP archive or if its content is
        different to that on GitHub. False otherwise.
        """
        if self.is_new_file():
            return True
        else:
            if self.is_data_file() and self._parsed is not True:
                self.parse()
                return any((self.new_ids(), self.modified_ids(),
                            self.deleted_ids()))
            else:
                return self.github_content() != self.file_content()

    def github_url(self):
        """
        Returns the URL for the raw version of this file GitHub currently has
        at the tip of the branch. Assumes the file resides in the ``data``
        sub-directory within the repo.
        """
        return "/".join(("https://raw.githubusercontent.com", GITHUB_USER,
                         GITHUB_REPO, GITHUB_BRANCH, "data",
                         self.zip_info.filename))

    def github_content(self):
        """
        Returns the contents of the raw version of this file GitHub currently
        has at the tip of the branch.
        """
        github_response = requests.get(self.github_url())
        return github_response.content

    def file_content(self):
        """Returns the contents of the this file in the ZIP archive."""
        return self.zip_file.open(self.zip_info).read()

    def parse(self):
        """
        Parses the file, storing unique ids and people's names for each row
        that has been added, modified, or deleted since the file was last
        committed and pushed to GitHub.

        Assumes data files are CSVs with unique ids in column 1 and people's
        names in column 2.
        """
        if not self.is_data_file():
            raise TypeError("{} is a data file".format(self.zip_info.filename))

        d = difflib.Differ()
        # Compare the version of this file on GitHub to the version of this
        # file in the ZIP archive, and creates a list of lines that have been
        # added or deleted, marking each as such.
        diffs = [
            (l[0], l[2:])
            for l in d.compare(
                self.github_content().decode("UTF-8").splitlines(),
                self.file_content().decode("UTF-8").splitlines()
            )
            if l[0] in ("+", "-")
        ]

        ids_to_name = {}
        new_ids = set()
        deleted_ids = set()

        # change_type is either "+" for rows that have been added or "-" for
        # rows that have been deleted.
        for change_type, line in diffs:
            # Treat each line as an individual CSV file.
            row = next(csv.reader(io.StringIO(line)))
            # Unique ids are in column 1.
            unique_id = int(row[0])
            # Names are in column 2.
            name = row[1]
            if change_type == "+":
                new_ids.add(unique_id)
                ids_to_name[unique_id] = name
            else:
                deleted_ids.add(unique_id)
                if unique_id not in ids_to_name:
                    ids_to_name[unique_id] = name

        # Modified rows are those whose ids are in both the new and deleted
        # rows.
        modified_ids = new_ids & deleted_ids
        # New rows are those whose ids are in the new set but not in the
        # deleted set.
        new_ids = new_ids - modified_ids
        # Deleted rows are those whose ids are in the deleted set but not in
        # the new set.
        deleted_ids = deleted_ids - modified_ids

        # Create lists of new, modified, and deleted unique ids and names.
        self.new_records = [(uid, ids_to_name[uid]) for uid in new_ids]
        self.modified_records = [(uid, ids_to_name[uid])
                                 for uid in modified_ids]
        self.deleted_records = [(uid, ids_to_name[uid]) for uid in deleted_ids]

        self._parsed = True

    def _ids(self, records):
        if self._parsed is not True:
            raise ValueError("{}.parse() must be called first".format(
                self.__class__.__name__))
        return [r[0] for r in records]

    def new_ids(self):
        """
        Return a list of unique ids, one for each row that's been added to the
        file.
        """
        return self._ids(self.new_records)

    def modified_ids(self):
        """
        Return a list of unique ids, one for each row that's been modified in
        the file.
        """
        return self._ids(self.modified_records)

    def deleted_ids(self):
        """
        Return a list of unique ids, one for each row that's been removed from
        the file.
        """
        return self._ids(self.deleted_records)

    def names(self, records):
        if self._parsed is not True:
            raise ValueError("{}.parse() must be called first".format(
                self.__class__.__name__))
        return [r[1] for r in records]

    def new_names(self):
        """
        Return a list of names, one for each row that's been added to the file.
        """
        return self.names(self.new_records)

    def modified_names(self):
        """
        Return a list of names, one for each row that's been modified in the
        file.
        """
        return self.names(self.modified_records)

    def deleted_names(self):
        """
        Return a list of names, one for each row that's been removed from the
        file.
        """
        return self.names(self.deleted_records)

    def _submessage(self, action, names):
        if len(names) == 1:
            message = "{} {}".format(action, names[0])
        else:
            if sum(map(len, names)) > 20:
                message = "{} {} and {} other{}".format(
                    action,
                    names[0],
                    len(names[1:]),
                    "s" if len(names) > 2 else ""
                )
            else:
                message = "{} {}".format(action, ", ".join(names))
        return message

    def message(self):
        """
        Returns a message suitable for using as a commit message that explains
        the changes in the file.
        """
        def sorted_names(names):
            """
            Move "Unknown" to the end of the list, but otherwise keep the order
            as-is.
            """
            return ([name for name in names if name != "Unknown"] +
                    [name for name in names if name == "Unknown"])

        if self.is_new_file():
            message = "Add {}".format(self.zip_info.filename)
        else:
            if self.is_data_file():
                message = []
                if self.new_ids():
                    names = sorted_names(self.new_names())
                    message = [self._submessage("add", names)]
                if self.modified_ids():
                    names = sorted_names(self.modified_names())
                    message.append(self._submessage("update", names))
                if self.deleted_ids():
                    names = sorted_names(self.deleted_names())
                    message.append(self._submessage("remove", names))
                message = "; ".join(message)
                message = message[0].upper() + message[1:]
            else:
                message = "Update {}".format(self.zip_info.filename)
        return message.strip() + "\n"

    def commit(self):
        """
        Commit this file to the GitHub repo. Limited to committing to the
        repo's default branch.

        Raises:
            ValueError: file has no changes
        """
        if self.is_dirty() is not True:
            raise ValueError("nothing to commit")
        gh = github3.login(token=os.getenv("GITHUB_TOKEN"))
        repo = gh.repository(GITHUB_USER, GITHUB_REPO)
        filename = "data/{}".format(self.zip_info.filename)
        if self.is_new_file():
            repo.create_file(filename, self.message(), self.file_content(),
                             branch=GITHUB_BRANCH)
        else:
            contents = repo.file_contents(filename, GITHUB_BRANCH)
            contents.update(self.message(), self.file_content())


def pushover(message):
    """Sends a push notification via Pushover."""
    from pushover import Client, InitError
    try:
        Client().send_message(message, title="Changes to the Counted",
                              url="https://github.com/{}/{}/commits/{}".format(
                                  GITHUB_USER, GITHUB_REPO, GITHUB_BRANCH))
    except InitError:
        pass


def get_zip():
    """
    Returns the contents of the ZIP archive of The Counted data, provided by
    the Guardian. The return value is the compressed ZIP bytes.

    Raises:
        requests.exceptions.HTTPError: request returned a 4xx or 5xx HTTP
            status code

    Returns:
        bytes
    """
    response = requests.get(
        SOURCE_URL,
        headers={"User-Agent": USER_AGENT}
    )
    response.raise_for_status()
    return response.content


def main():
    """
    Downloads the latest "The Counted" data from the Guardian, commits any data
    changes to a GitHub repo, and, if there are changes, reports the results
    via a push notification.
    """
    with io.BytesIO(get_zip()) as fh, CountedZipFile(fh) as zf:
        if True or zf.is_dirty():
            for data in zf.files():
                if data.is_dirty():
                    data.commit()
            message = []
            for func, action in (("new_names", "added"),
                                 ("modified_names", "updated"),
                                 ("deleted_names", "deleted")):
                names = getattr(zf, func)()
                if names:
                    message.append("{} {} {}".format(
                        len(names), "people" if len(names) > 1 else "person",
                        action))
            pushover(", ".join(message))


if __name__ == "__main__":
    main()
