### Quick Start

1. Clone the repository and go to folder

2. Initialize and activate a virtualenv:
  ```
  py -m venv venvname
  venvname/Scripts/activate
  ```

3. Install the dependencies:
  ```
  install -r requirements.txt
  ```

5. Run the development server:
  ```
  py main.py
  ```

6. Navigate to [http://localhost:5000](http://localhost:5000)

### Description
The project has two pages: Main page and Users page. You must be logged in to access the site.
At the first start, admin is automatically created:
Login: admin
Password: admin
You can register a new user from on the SignIn page. A new user is created with a basic level of access: view the list of users only.
Admin can delete users, change access level, user password, user description on the User page.
You cannot remove the admin and you cannot change the admin access level, but you can change the password.

Any user can log out of a session by clicking the SignOut button.