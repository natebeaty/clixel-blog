+++
date = "2019-05-21"
title = "Gitlog Automagical Timesheet Filler Outer Redux"
slug = "gitlog-automagical-timesheet-filler-outer-redux"
layout = "blog"
+++
I've been using variations on this script for several years to spit out my git commit log in a timesheet-friendly format, [initially just as a single command](https://blog.clixel.com/post/111391696763/daily-git-log-for-your-timesheet).

I've now refined it to a [li'l bash script](https://gist.github.com/natebeaty/b3edf108434a2d16cc600bd0686e92a8) that has a few extra tricks up its sleeve (updated yet again in 2025):

```
#!/bin/bash
# Pulls git log entries for a day formatted for pasting in a timesheet

# Usage:
# gitlog = all commits today
# gitlog -2 = all commits -2 days ago
# gitlog 2024-10-03 or 10/3/2024 or 10-3

args=$1
# Replace / with - in args for alternate date formats e.g. 10/3/2024
args=${args//\//\-}

# Default day to today if no args are sent
day=`date +%F`

# Convert various argument formats to YYYY-MM-DD
if [[ $args =~ ^[0-9]{1,4}\-[0-9]{1,2}\-[0-9]{1,2}$ ]]; then
	# already in format needed
	day=$args
elif [[ $args =~ ^[0-9]{1,2}\-[0-9]{1,2}$ ]]; then
	# 10-10 -> 2024-10-10
	day=`date -jf %m-%d +%Y-%m-%d $args`
elif [[ $args =~ ^[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{1,4}$ ]]; then
	# 10-10-2024 -> 2024-10-10
	day=`date -jf %m-%d-%Y +%Y-%m-%d $args`
elif [[ $args =~ ^\-[0-9]{1,2}$ ]]; then
	# -2 (days ago)
	day=`date -v"$args"d +%F`
fi

# Store output to var so we can spit it out to console then shove it in the clipboard
logs=$(git log --all --author="`git config user.name`" --no-merges --format="%s %ai" | grep $day | perl -pe 's/ (\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2} \-\d{4})//g' | perl -pe 's/^(compiled assets|pedant|cleanup|typo)\n$//g' | tail -r | perl -pe 's/\n/; /' | sed -e "s/; $//g")

if [ "$logs" = "" ]; then
	echo "No git logs found for $day"
else
	echo -e "Log for $day (also in clipboard):\n----\n$logs"
	echo -e $logs | pbcopy
fi
```

You set your name in the script, drop it in your `~/bin` dir and `chmod +x` it, then run `gitlog` from a repo dir with various options, the default being the current day. Use `gitlog -1` to show commits from yesterday, or `gitlog 2025-01-01` to show a specific date. Your git commit messages are concatenated in a format suitable for timesheets, ready to be pasted into whatever time-tracking program you prefer. e.g.:

```
$ gitlog
Log for 2025-02-20 (also in clipboard):
----
slight copy edits; update highlightjs and change theme to agate; host highlightjs locally; simple dark theme
```
