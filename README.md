# Renren Backup

Back up your renren statuses and render them as plain HTML.

## Usage

To backup your renren.com status, run:

```
python backup_renren_status.py <user_email> [<user_password>|-p]
```

where `user_email` and `user_password` are your renren.com login credentials. If you prefer non-explicit password, you can use -p to get a prompt, which hides the input.

To render your statuses, run:

```
python render_status.py <status_directory>
```

where `status_directory` is the directory of downloaded status json files.

## Dependencies

The dependencies are listed in requirements.txt. You can use `pip` to install them.
