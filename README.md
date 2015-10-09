# What's The Counted?

To quote from [the Guardian] [1]:

> The Counted is a project by the Guardian --- and you --- working to count the number of people killed by police and other law enforcement agencies in the United States throughout 2015, to monitor their demographics and to tell the stories of how they died.

# And what's this?

The Guardian makes the data behind the project [available as a ZIP file] [2] and they keep that file up-to-date, but they don't give any indication when that file changes nor what's changed when it does.

Fortunately, the ZIP file's contents are a [README] [3] and a [CSV file] [4], which are well-suited to being stored in Git. And since the zipped data is available on the Web it's also easy to check that regularly to see if it's changed.

That's where this comes in: the ZIP file is checked every twenty minutes for changes, and if there's anything new it's committed to a local copy of this repository and then pushed to GitHub. By keeping track of this repo you can ensure you have the latest version of the data behind The Counted.

## Repository contents

Data extracted from the source ZIP file is kept in the [`data` directory] [5] on the master branch. No alterations are made to the files themselves and all the hard work is done by the Guardian's staff. Everything outside of the `data` directory is _not_ part of the source data and is only there to support keeping it in this repo.

# Keeping track of the data

The nerdiest way is to clone the repository and pull regularly, but if you're not of the nerd persuasion then you have a few other options:

* If you have an account on GitHub you can [watch the repository] [6]. Changes to the repo will then appear on [your dashboard] [7] when you're logged in
* If you don't have an account on GitHub you can bookmark the [commits page] [8]. New messages there mean new updates to the repo
* You can subscribe to the [Atom (like RSS) feed] [9]. Any updates to the repo will then appear in your feed reader of choice

# Support

* Home page: https://github.com/flother/thecounted
* Issues: https://github.com/flother/thecounted/issues

[1]: http://www.theguardian.com/us-news/ng-interactive/2015/jun/01/about-the-counted
[2]: https://interactive.guim.co.uk/2015/the-counted/thecounted-data.zip
[3]: https://raw.githubusercontent.com/flother/thecounted/master/data/README.txt
[4]: https://raw.githubusercontent.com/flother/thecounted/master/data/the-counted.csv
[5]: https://github.com/flother/thecounted/tree/master/data
[6]: https://github.com/flother/thecounted/watchers
[7]: https://github.com/
[8]: https://github.com/flother/thecounted/commits/master
[9]: https://github.com/flother/thecounted/commits/master.atom

