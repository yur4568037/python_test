### Quick Start

1. Clone the repository and go to folder

2. Initialize and activate a virtualenv:
  ```
  py -m venv venvname
  venvname/Scripts/activate
  ```
If the system does not allow script execution, then you need to run Powershell as an administrator and run the command:
  ```
  Set-ExecutionPolicy RemoteSigned
  ```

3. Install the dependencies:
  ```
  pip install -r requirements.txt
  ```

5. Run the development server:
  ```
  py main.py
  ```

6. Navigate to [http://localhost:5000](http://localhost:5000)

### Description
The project has three pages: Main page, Users page and Database. You must be logged in to access the site.
At the first start, admin is automatically created:
Login: admin
Password: admin
You can register a new user from on the SignIn page. A new user is created with a basic level of access: view the list of users only.
Admin can delete users, change access level, user password, user description on the User page.
You cannot remove the admin and you cannot change the admin access level, but you can change the password.
Access level:
1 - admin
2 - user
Any user can log out of a session by clicking the SignOut button.

The Database page displays information received from three HTTP data points (processed by the same program). When you click on the Request button, the server initiates a one-time asynchronous polling of data points. The received information is sorted by id and displayed on the screen.
