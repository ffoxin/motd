# Show docker container status upon login after motd

## How to use

1. Create python3 virtualenv
  ```
  python3 -m venv venv
  ```
1. Install requirements
  ```
  venv/bin/pip install -r requirements.txt
  ```
1. Add to the end of profile file:
  ```
  /path/to/system-info.sh
  ```

### bash
Profile file - `/etc/profile`

### zsh
Profile file - `/etc/zsh/zprofile`
