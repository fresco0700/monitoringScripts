import requests

def get_tomcat_apps_status():
    url = "http://localhost:8080/manager/text/list"
    username = "script"
    password = "tomcat"

    response = requests.get(url, auth=(username, password))

    if response.status_code == 200:
        app_data = response.text.strip().split('\n')[1:]
        app_status = {}

        for line in app_data:
            parts = line.split(':')
            app_name = parts[0]
            status = parts[1]
            app_status[app_name] = status

        return app_status
    else:
        print("Failed to fetch data from Tomcat Manager API.")
        return None

def main():
    app_status = get_tomcat_apps_status()

    if app_status:
        for app_name, status in app_status.items():
            if status == 'running':
                print(f"Application {app_name} is running.")
            else:
                print(f"Application {app_name} is not running.")

if __name__ == "__main__":
    main()