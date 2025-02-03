---
title: "Implementing PHP Background Tasks With Beanstalk"
date: 2025-01-28
slug: "2025-01-28-implementing-php-background-tasks"
---

![a bunch of terminal log output with silly graphics on top conveying computer consternation](/images/beanstalkin.jpg)

I have a sprawling custom PHP codebase for a client that I started nearly a quarter century ago (!!), which has rapidly been increasing in complexity with database-intensive caching of various aggregate sums for customers and orders, a complex stock report / on order pipeline for products + distributors in various warehouse locations, and more long-running email + API operations that I'd like to keep out of the normal web request cycle. 

Over the years, I slowly expanded on a rudimentary delayed task queue, with several periodically run cronjobs which query a `cronjobs` table for matching tasks based on `type`, `item_id` and `date_added` fields. This has worked well for all sorts of needs, especially when accumulating a list of long-running tasks to do in batches late at night or every few hours, but I've found myself having more urgent background tasks that need to run more quickly than "sometime in the next 1-60 seconds." The user needs to see results from their actions within a few seconds, or they'll think it isn't working. I considered querying `cronjobs` and showing users a notice like _"Hey! There's a pending update for this item. Refresh in a minute or two to see changes."_ — but that just feels dumb. Also, managing the lifecycle and schedules of application <-> mysql <-> stand-alone script <-> cronjob is a pain and annoyingly distributed (e.g., cronjob entries aren't stored in git).[^1]

After much searching around, I first tried [Gearman](https://gearman.org/) since it had been around so long, assuming it was feature complete and solid. Overall it was pretty simple to set up, but it was a bit of a mess trying to get it running locally on my M1 MacBook, where I use homebrew to switch between a few versions of PHP[^2]. I kept having a "Please install libgearman" error barfed up when running `pecl install gearman`. I tried all sorts of fixes until [I realized](https://stackoverflow.com/questions/9705925/how-to-install-gearman-extension-on-mamp/16295084#comment139990831_16295084) I could easily install it from source (duh! c'mon Nate), allowing me to specify necessary homebrew paths with `./configure --with-php-config=/opt/homebrew/opt/php@8.3/bin/php-config --with-gearman=$(brew --prefix gearman)`. 

Once I had it running, I was able to set up a few worker classes and fired up [Gearman Manager](https://github.com/brianlmoon/GearmanManager) to handle daemonizing. Everything was working great until I realized I have some workers I would like to queue up in the future, and a few searches later I realized that would introduce even *more* dependencies for me to manage, possibly even reverting to using my `cronjob` setup with some tweaks for async tasks. I really wanted to keep this as simple and self-contained as possible.[^3] 

While searching around for delayed queue support in Gearman, I saw mention of [Beanstalk](https://beanstalkd.github.io/) as an alternative which supported future-dated tasks. It also seemed like Beanstalk was a bit more straightforward. Ok! Tear it all down! Let's try this again!

Switching to Beanstalk was pretty painless, but ironically there was an aspect of Gearman that it *didn't* support: unique keys for each task, to avoid queueing up duplicates. I saw a suggested solution that reminded me of what I was just trying to avoid: setting up your own middleware to track keys and avoid duplication. Argh! I decided to worry about it later.[^4] 

I started with two workers, one for order-related hooha, and one for stock report giggles. The workers basically look like this:

```
<?php
require(__DIR__.'/bootstrap.php');

use Pheanstalk\Pheanstalk;
use Pheanstalk\Values\TubeName;

$pheanstalk = Pheanstalk::create($_ENV['BEANSTALKD_SERVER']);
$tube = new TubeName('orders');
$pheanstalk->watch($tube);

// This hangs until a Job is produced
$job = $pheanstalk->reserve();

try {

  $data = json_decode($job->getData(), true);

  // Merge in "force-run" flag to opts to trigger running task immediately
  $opts = array_merge(($data['opts'] ?? []), [
    'force-run' => 1
  ]);

  // Run method with 'force-run' flag + original params
  APP()->orders->doFooBar($opts);

  // Delete job from queue
  $pheanstalk->delete($job);

} catch(\Exception $e) {
  
  $error_msg = $e->getMessage();

  // If mysql timed out, no need to log error, just release for next worker
  if (!preg_match('/MySQL server has gone away/i', $error_msg)) {
    echo sprintf("%s: Error running Job %s (#%s): %s\n", date('Y-m-d H:i:s'), $data['task'], $job->getId(), $error_msg);
  }

  // Let another worker retry this job
  $pheanstalk->release($job);

}
```

I manage these workers with Supervisor, configured in `/etc/supervisor/conf.d/workers.conf`:

```
[program:orders]
command=/usr/bin/php /var/www/app/workers/%(program_name)s.php
process_name=%(program_name)s_%(process_num)02d
stdout_logfile=/var/logs/supervisor/%(program_name)s.log
stderr_logfile=/var/logs/supervisor/%(program_name)s-error.log
user=www-data
autostart=true
autorestart=true
numprocs=3
startsecs=0

[program:stock-report]
command=/usr/bin/php /var/www/app/workers/%(program_name)s.php
process_name=%(program_name)s_%(process_num)02d
stdout_logfile=/var/logs/supervisor/%(program_name)s.log
stderr_logfile=/var/logs/supervisor/%(program_name)s-error.log
user=www-data
autostart=true
autorestart=true
numprocs=3
startsecs=0
```

I was having issues keeping workers alive, as many of my "long-running" tasks turned out to be *much* quicker than supervisor liked, and it would stop respawning after a few requests (by default, `startretries=3`). These tasks hang while waiting for a job, but as soon as a job enters the queue, they process it and quit in a fraction of a second. Supervisor was upset until I added `startsecs=0` to the config, which specifies "the number of seconds a program must stay running after a startup to be considered successfully started." 

Originally I thought these would be daemon processes, and I might switch to that method, using a `while` statement with `sleep` after each job to keep it from hogging CPU. But for now, it seems to be working fine to just fire up a new process to handle each job.

I set up several of my existing methods that I want to support async with a `force-run` flag. If it's not present, they will add the task to a Beanstalk queue[^5] with a JSON string of the params and return. The worker then appends `force-run` to the params, and runs the same method in the background process. 

Everything has been working well for a first dabble in background/async tasks. I had a hard time finding comprehensive explanations of the entire setup + configs, so hopefully this helps any other poor sucker hacking away at a custom PHP stack. 

[^1]: All said, my homegrown crontab system is still in use for several scripts. I could improve the system by having a central cron pipeline, and only one `check-pending-cronjobs` script that runs every minute. It just hasn't hit that threshold of pain yet to inspire refactoring.
[^2]: I have tried several times to get on the Docker train, but it always seems to introduce more problems than solutions for my local development setup. I just have so many legacy projects + a handful of more modern Craft/Statamic sites, and for the most part they all work fine sharing the same instances of Apache/MariaDB/PHP 8.x.
[^3]: I tend to dive into all sorts of obscure tech solutions, learn enough to get it working for my needs, then not touch for a year or more. When I come back to it I have to reverse engineer my own dang work. I do leave copious comments everywhere for future Nate, but that doesn't help much when I invariably have to run updates and suddenly there are incompatibilities and changes that make my old notes useless.
[^4]: Looking back now, I realize this isn't worth worrying about, as most of my tasks run immediately, and *should* run again if a duplicate is queued up soon afterward.
[^5]: Only if Beanstalk is running, otherwise it just runs the method immediately. This allows the staging site to not require its own set of supervisor'd PHP processes constantly running.
