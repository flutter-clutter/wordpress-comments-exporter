# wp\_comment\_exporter

Congratulations on your decision of migrating from [Wordpress](http://wordpress.org) to [Hugo](https://gohugo.io/)!  
Oh, you haven't? [Here](https://www.flutterclutter.dev/news/2022-03-21-migration-to-hugo/) are some reasons. 

You may have already noticed the export from Wordpress is quite ugly and hard to parse.

Luckily, this fantastic community provides tome tools for this task.  
The post export worked out quite well using [this tool](https://github.com/SchumacherFM/wordpress-to-hugo-exporter), but I struggled with the comments.

That's why I wrote my own tool for this.

The output are `yaml` files that can be e. g. used by [Staticman](https://staticman.net/).

So basically this tool takes a wordpress export and converts it to this:

(in `output/my-post-id/comment-1628575290.yml`)

```yaml
_id: '1'
comment: 'Wow, I used to me a Wordpress comment. I\'m finally free!'
date: '2022-04-04 08:01:30'
email: christian@commenter.com
email_hash: 9b77b628098cfa13f8e96da3d03ff548
name: Christian Commenter
```

## Requirements

You only need [Docker](https://www.docker.com/) for this.

## Usage

1. Put the [Wordpress export XML files](http://en.blog.wordpress.com/2006/06/12/xml-import-export/) into a directory called `input` in the project directory
2. Copy the `.env.example` file to `.env`: `cp .env.example .env`
3. Insert the URL of the Wordpress site you want to export the comments from in your `.env` file. This is necessary to extract the id from the post, which is used as the directory for the comment
4. Run `docker-compose up`
5. Find the `yaml` files in the `output` directory within their respective directories