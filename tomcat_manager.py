import argparse
import requests

TOMCAT_MANAGER_URL = "http://localhost:8080/manager/text/"
TOMCAT_USERNAME = "script"
TOMCAT_PASSWORD = "tomcat"


def get_app_status(app_name):
    response = requests.get(
        f"{TOMCAT_MANAGER_URL}/list",
        auth=(TOMCAT_USERNAME, TOMCAT_PASSWORD)
    )
    if response.status_code == 401:
        print("Błędne poświadczenia")
        exit(1)
    app_lines = response.text.splitlines()
    for line in app_lines:
        if line.startswith(f"/{app_name}:"):
            return "running" if ":running:" in line else "stopped"
    return "Nie znaleziono"

def list_apps():
    try:
        response = requests.get(
            f"{TOMCAT_MANAGER_URL}/list",
            auth=(TOMCAT_USERNAME, TOMCAT_PASSWORD)
        )
        if response.status_code == 401:
            print("Błędne poświadczenia")
            exit(1)
        return response.text
    except Exception:
        print("Wystąpił problem z połączeniem")
        exit(1)


def manage_app(action, app_name):
    # Ekstrakcja contextPath i version z app_name
    context_path, version = app_name.split(";")

    app_status = get_app_status(context_path)

    # Jeśli aplikacja nie została znaleziona, nie powinniśmy blokować akcji stop.
    if app_status == "Nie znaleziono" and action == "stop":
        print(f"Error: Aplikacja '{context_path}' nie została znaleziona.")
        return

    # Jeśli aplikacja jest już w stanie running i próbujemy ją uruchomić
    if app_status == "running" and action == "start":
        print(f"Error: Aplikacja '{context_path}' jest już uruchomiona.")
        return

    # Jeśli aplikacja nie jest w stanie running i próbujemy ją zatrzymać
    if app_status == "stopped" and action == "stop":
        print(f"Error: Aplikacja '{context_path}' jest już zatrzymana.")
        return

    try:
        response = requests.get(
            f"{TOMCAT_MANAGER_URL}/{action}",
            params={
                "path": f"/{context_path}",
                "version": version
            },
            auth=(TOMCAT_USERNAME, TOMCAT_PASSWORD)
        )
        return response.text
    except Exception:
        print("Wystąpił problem z połączeniem")
        exit(1)

def main():
    if not TOMCAT_MANAGER_URL or not TOMCAT_USERNAME or not TOMCAT_PASSWORD:
        print("Error: Zmienne TOMCAT_MANAGER_URL, TOMCAT_USERNAME, TOMCAT_PASSWORD muszą zostac zdefiniowane.")
        return
    parser = argparse.ArgumentParser(description="Tomcat python Manager "
                                                 " Skrypt potrzebuje dostępu do manager-script,"
                                                 " aby go ustawić należy dodac linie:"
                                                 " <user username=\"<LOGIN>\" password=\"<HASLO>\" roles=\"manager-script\"/>"
                                                 " Do pliku: "
                                                 "/tomcat/conf/tomcat-users.xml")
    parser.add_argument("action", choices=["start", "stop", "reload", "list"], help="Akcja do wykonania")
    parser.add_argument("app_name", nargs="?", help="Name of the application")

    args = parser.parse_args()

    if args.action == "list":
        app_list = list_apps()
        print(app_list)
    elif not args.app_name:
        print(f"Error: Nazwa aplikacji jest wymagana do wykonania akcji {args.action}")
    else:
        result = manage_app(args.action, args.app_name)
        print(result)

if __name__ == "__main__":

    main()
