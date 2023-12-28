# notion2md

> use offical notion api with [**notion_client**](https://github.com/ramnes/notion-sdk-py)

Convert multiple notion pages to markdown files and try to keep the formatting usable.

## Usage

don't need download repo, get your Token and export your page:

1. get Internal Integration Token  
   In [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations), create your workspace integration and get token, like `secret_...`

2. download package with pip3

```python
pip3 install notion-md
```

3. set env variable or input in your terminal:

```shell
export NOTION_TOKEN=your token
export NOTION_PAGES=your main page link
```

you can select a seperate open page for downloading, and put others page links in this page(use Notion: `/Link` command). Then get this page link, **make sure you add the integration to your workspace and all your pages your would export.**

4. download files use **notion_md** command:

```shell
notion_md
```

pages are saved to **notion2md_files dir**, default only download files storaged in notion.

## surpported

export markdown files for [Gridea](https://gridea.dev/)-like blog side, supporting properties of notion database pages eg. Tags, Cover.

- [x] normal block(header,list,code,quote,...)
- [x] link page/sub page
- [x] table
- [x] callout
- [x] inline_database(pages)
- [x] image/youtube video/file
- [x] file download(files in notion)

## notes

- **`multi-level list items`, `bookmarks`, etc. make synchronous network requests, which take longer than other blocks**.
- only download files in notion, external links will be ignored.
- for database, only download pages in the database.
- children blocks in callouts will be ignored, simple style is better.

