###

Python 3.6 or later required

### Before

0. Install plugin `application-passwords` (for image uploading)
    ```text
    https://wordpress.org/plugins/application-passwords/
    ```

1. Get (create) new WP REST API credential `(username/password)` for user
    ```text
    WP_admin_panel 
    -> Users (menu item)
    -> pick (click) (or create and pick) admin user 
    -> create new credentials (Application Passwords will be at the bottom) 
    -> remember login and password
    ```

### Instructions

0. Clone project into `/var/www/html` (WP root directory)
    ```bash
    git clone this_project_path
    ```

1. Add to env variable `$PYTHONPATH` root_dir
    ```bash
    export PYTHONPATH=$PYTHONPATH:/var/www/html 
    ```

2. Install python lib (from directory: `/var/www/html`) 
    ```bash
    pip install -r requirements.txt
    ```

3. Edit config  
    ! Don't forget to add the username and password obtained from application-passwords !  
    Thus need check (and edit if necessary) `# MySQL` and `# REST API CREDENTIALS` config parts
    ```text
    path = /var/www/html/config.py
    ```

### Run function
Two variants:

1. Import from `rental.py` (path - `/var/www/html/rental.py`)
    ```text
    from rental import parse_property
   
    parse_property(36325, '32' 'de')
    ```

2. Run from cmd (terminal)  
    If the server does not have python version 3, replace `python3` with `python` 
    ```bash
    python3 rental.py <payload_number:int> <post_id:str> <lang:str> 
    ```
   Example with real values
    ```bash
    python rental.py 36325 32 de
    ```

### Function params

1. payload_number
    - Type: integer
    - If there are not real payload number with this number - an exception will be thrown
2. post_id
    - Type string
3. lang
    - Type string (2 char)
    - Checked (`de`, `en`, `fr`, `it`)
