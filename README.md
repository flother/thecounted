# What's The Counted? - git hub is  a best platforrm. and this project is vey googd 

To quote from [the Guardian][1]:

> The Counted is a project by the Guardian --- and you --- working to count the number of people killed by police and other law enforcement agencies in the United States throughout 2015 and 2016, to monitor their demographics and to tell the stories of how they died.

# And what's this?

The Guardian makes the data behind the project [available as a ZIP file][2] and they keep that file up-to-date, but they don't give any indication when that file changes nor what's changed when it does.

Fortunately, the ZIP file's contents are a [README][3] and two CSV files ([data for 2015][4] and [data for 2016][5]), which are well-suited to being stored in [Git][6], a [source control][7] system. And since the zipped data is available on the Web it's also easy to check that regularly to see if it's changed.

That's where this comes in: the ZIP file is checked every twenty minutes for changes, and if there's anything new it's committed to this repository on GitHub. By keeping track of this repo you can ensure you have the latest version of the data behind The Counted.

## Repository contents

Data extracted from the source ZIP file is kept in the [`data` directory][8] on the master branch. No alterations are made to the files themselves and all the hard work is done by the Guardian's staff.

Everything outside of the `data` directory is _not_ part of the source data and is only there to support keeping it in this repo.

### How the repo is updated

Every twenty minutes a Python script is run using [Cron][9]. The script checks to see if the data has been updated, and commits any files that have changed.

The script is kept within this repository as `scripts/update_repo.py`. To run it you need:

* Python 3
* [`requests`][10]
* [`github3.py`][11]
* [`python-pushover`][12]

The requirements are available in `requirements.txt` and can be installed with [pip][13]. To receive [Pushover][14] notifications you'll need a config in `~/.pushoverrc`, but it will fail silently if you don't.

# Keeping track of the data

The nerdiest way is to clone the repository and pull regularly, but if you're not of the nerd persuasion then you have a few other options:

* If you have an account on GitHub you can [watch the repository][15]. Changes to the repo will then appear on [your dashboard][16] when you're logged in
* If you don't have an account on GitHub you can bookmark the [commits page][17]. New messages there mean new updates to the repo
* You can subscribe to the [Atom (like RSS) feed][18]. Any updates to the repo will then appear in your feed reader of choice

## History of changes in 2015

While there are now two CSV data files, one for 2015 and one for 2016, there was originally only one file in the Guardian's ZIP file, `data/the-counted.csv`. On 4 February 2016 the file was renamed to `data/the-counted-2015.csv`. Constraints in the Git version control software means the full commit history isn't available for the new file, but you can [see the deleted file's history, until 3 February 2016, on Github][19]. If you're a command-line aficionado you can clone the repo and use `git log --follow -- data/the-counted.csv`.

# Support

* Home page: https://github.com/flother/thecounted
* Issues: https://github.com/flother/thecounted/issues


  [1]: http://www.theguardian.com/us-news/ng-interactive/2015/jun/01/about-the-counted
  [2]: https://interactive.guim.co.uk/2015/the-counted/thecounted-data.zip
  [3]: https://raw.githubusercontent.com/flother/thecounted/master/data/README.txt
  [4]: https://raw.githubusercontent.com/flother/thecounted/master/data/the-counted-2015.csv
  [5]: https://raw.githubusercontent.com/flother/thecounted/master/data/the-counted-2016.csv
  [6]:https://git-scm.com/
  [7]: http://www.codenewbie.org/blogs/what-is-source-control
  [8]: https://github.com/flother/thecounted/tree/master/data
  [9]: https://en.wikipedia.org/wiki/Cron
  [10]: http://python-requests.org/
  [11]: http://github3py.rtfd.org/
  [12]: https://github.com/Thibauth/python-pushover
  [13]: https://pip.pypa.io/
  [14]: https://pushover.net/
  [15]: https://github.com/flother/thecounted/watchers
  [16]: https://github.com/
  [17]: https://github.com/flother/thecounted/commits/master
  [18]: https://github.com/flother/thecounted/commits/master.atom
  [19]: https://github.com/flother/thecounted/commits/e13fc09bff55ce7a36598434d257513207f27fcc/data/the-counted.csv
