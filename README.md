# iCloud Photos Display

A web view that show photo downloaded from iCloud

## Usage

With Docker using the following command:

```
docker run -it --rm --name icloudpd -v $(pwd)/Photos:/data -e TZ=America/London tomcuzz/icloudpd:latest icloud-photo-display --directory /data --username my@email.address --watch-with-interval 3600
```

## Credits

The code to download photos from iCloud was forked from [icloud-photos-downloader/icloud_photos_downloader](https://github.com/icloud-photos-downloader/icloud_photos_downloader)
