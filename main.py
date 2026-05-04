import csv
import json
from connect import get_connection


def get_group_id(cur, group_name):
    cur.execute(
        "INSERT INTO groups(name) VALUES(%s) ON CONFLICT (name) DO NOTHING",
        (group_name,)
    )
    cur.execute(
        "SELECT id FROM groups WHERE name = %s",
        (group_name,)
    )
    return cur.fetchone()[0]


def print_rows(rows):
    if not rows:
        print("Nothing found.")
        return

    for row in rows:
        print(
            f"ID: {row[0]} | Name: {row[1]} | Email: {row[2]} | "
            f"Birthday: {row[3]} | Group: {row[4]} | "
            f"Phone: {row[5]} ({row[6]}) | Created: {row[7]}"
        )


def add_contact():
    name = input("Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    phone_type = input("Phone type (home/work/mobile): ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group_name = input("Group (Family/Work/Friend/Other): ")

    conn = get_connection()
    if not conn:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                group_id = get_group_id(cur, group_name)

                cur.execute(
                    """
                    INSERT INTO contacts(name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE
                    SET email = EXCLUDED.email,
                        birthday = EXCLUDED.birthday,
                        group_id = EXCLUDED.group_id
                    RETURNING id
                    """,
                    (name, email, birthday, group_id)
                )
                contact_id = cur.fetchone()[0]

                # Use stored procedure to add phone
                cur.execute(
                    "CALL add_phone(%s, %s, %s)",
                    (name, phone, phone_type)
                )

        print("Contact added successfully!")

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def show_contacts():
    conn = get_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.name,
                    c.email,
                    c.birthday,
                    g.name,
                    p.phone,
                    p.type,
                    c.created_at
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                ORDER BY c.id
                """
            )
            rows = cur.fetchall()
            print("\n--- Contacts ---")
            print_rows(rows)

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def move_to_group():
    name = input("Contact name: ")
    group_name = input("New group: ")

    conn = get_connection()
    if not conn:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                # Use stored procedure
                cur.execute("CALL move_to_group(%s, %s)", (name, group_name))

        print("Contact moved to group!")

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def update_phone():
    name = input("Contact name: ")
    phone = input("New phone: ")
    phone_type = input("Phone type (home/work/mobile): ")

    conn = get_connection()
    if not conn:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE phones
                    SET phone = %s,
                        type = %s
                    WHERE contact_id = (SELECT id FROM contacts WHERE name = %s)
                    """,
                    (phone, phone_type, name)
                )

        print("Phone updated!")

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def search_contacts():
    query = input("Search by name/email/phone/group: ")

    conn = get_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Use stored function
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()

            # Reformat to match print_rows: id, name, email, birthday, group, phone, type, created_at
            # search_contacts returns: contact_name, email, birthday, group_name, phone, phone_type
            formatted = []
            for r in rows:
                formatted.append(("—", r[0], r[1], r[2], r[3], r[4], r[5], "—"))

            print("\n--- Search results ---")
            print_rows(formatted)

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def filter_by_group():
    group_name = input("Group name: ")

    conn = get_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.name,
                    c.email,
                    c.birthday,
                    g.name,
                    p.phone,
                    p.type,
                    c.created_at
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                WHERE g.name ILIKE %s
                ORDER BY c.id
                """,
                ("%" + group_name + "%",)
            )
            rows = cur.fetchall()
            print("\n--- Group filter results ---")
            print_rows(rows)

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def search_by_email():
    email_part = input("Email search: ")

    conn = get_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.name,
                    c.email,
                    c.birthday,
                    g.name,
                    p.phone,
                    p.type,
                    c.created_at
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                WHERE c.email ILIKE %s
                ORDER BY c.id
                """,
                ("%" + email_part + "%",)
            )
            rows = cur.fetchall()
            print("\n--- Email search results ---")
            print_rows(rows)

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def sort_contacts():
    print("Sort by:")
    print("1 - name")
    print("2 - birthday")
    print("3 - date added")

    choice = input("Choose: ")

    # FIX: use a whitelist dict instead of f-string interpolation (SQL injection)
    order_options = {
        "1": "c.name",
        "2": "c.birthday",
        "3": "c.created_at"
    }

    order_by = order_options.get(choice)
    if not order_by:
        print("Invalid choice")
        return

    conn = get_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    c.id,
                    c.name,
                    c.email,
                    c.birthday,
                    g.name,
                    p.phone,
                    p.type,
                    c.created_at
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                ORDER BY {order_by}
                """
            )
            rows = cur.fetchall()
            print("\n--- Sorted contacts ---")
            print_rows(rows)

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def paginated_navigation():
    limit = int(input("Page size: ") or 5)
    page = 0

    # FIX: open connection once, reuse across pages
    conn = get_connection()
    if not conn:
        return

    try:
        while True:
            offset = page * limit

            with conn.cursor() as cur:
                # Use stored function
                cur.execute(
                    "SELECT * FROM get_contacts_paginated(%s, %s)",
                    (limit, offset)
                )
                rows = cur.fetchall()

                # get_contacts_paginated returns: contact_name, email, birthday, group_name, phone, phone_type
                formatted = []
                for r in rows:
                    formatted.append(("—", r[0], r[1], r[2], r[3], r[4], r[5], "—"))

                print(f"\n--- Page {page + 1} ---")
                print_rows(formatted)

            command = input("\nn - next, p - previous, q - quit: ")

            if command == "n":
                page += 1
            elif command == "p":
                if page > 0:
                    page -= 1
            elif command == "q":
                break
            else:
                print("Invalid command")

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def export_to_json():
    filename = input("JSON filename to export: ") or "contacts_export.json"

    conn = get_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.name,
                    c.email,
                    c.birthday,
                    g.name,
                    p.phone,
                    p.type
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                ORDER BY c.id
                """
            )
            rows = cur.fetchall()

            # Group phones per contact
            contacts_dict = {}
            for name, email, birthday, group_name, phone, phone_type in rows:
                if name not in contacts_dict:
                    contacts_dict[name] = {
                        "name": name,
                        "email": email,
                        "birthday": str(birthday) if birthday else None,
                        "group": group_name,
                        "phones": []
                    }
                if phone:
                    contacts_dict[name]["phones"].append({"phone": phone, "type": phone_type})

            result = list(contacts_dict.values())

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

        print("Exported to", filename)

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def import_from_json():
    filename = input("JSON filename to import: ") or "contacts.json"

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as error:
        print("File error:", error)
        return

    conn = get_connection()
    if not conn:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                for item in data:
                    name = item["name"]
                    email = item.get("email")
                    birthday = item.get("birthday")
                    group_name = item.get("group", "Other")

                    group_id = get_group_id(cur, group_name)

                    cur.execute(
                        """
                        INSERT INTO contacts(name, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (name) DO UPDATE
                        SET email = EXCLUDED.email,
                            birthday = EXCLUDED.birthday,
                            group_id = EXCLUDED.group_id
                        """,
                        (name, email, birthday, group_id)
                    )

                    phones = item.get("phones", [])
                    if not phones:
                        phone = item.get("phone")
                        phone_type = item.get("phone_type", "mobile")
                        if phone:
                            phones = [{"phone": phone, "type": phone_type}]

                    for p in phones:
                        cur.execute(
                            """
                            INSERT INTO phones(contact_id, phone, type)
                            VALUES ((SELECT id FROM contacts WHERE name = %s), %s, %s)
                            """,
                            (name, p["phone"], p["type"])
                        )

        print("JSON import completed!")

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def import_from_csv():
    filename = input("CSV filename: ") or "contacts.csv"

    conn = get_connection()
    if not conn:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                with open(filename, "r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)

                    for row in reader:
                        name = row["name"]
                        email = row["email"]
                        birthday = row["birthday"]
                        group_name = row["group"]
                        phone = row["phone"]
                        phone_type = row["type"]

                        group_id = get_group_id(cur, group_name)

                        cur.execute(
                            """
                            INSERT INTO contacts(name, email, birthday, group_id)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (name) DO UPDATE
                            SET email = EXCLUDED.email,
                                birthday = EXCLUDED.birthday,
                                group_id = EXCLUDED.group_id
                            """,
                            (name, email, birthday, group_id)
                        )

                        cur.execute(
                            """
                            INSERT INTO phones(contact_id, phone, type)
                            VALUES ((SELECT id FROM contacts WHERE name = %s), %s, %s)
                            """,
                            (name, phone, phone_type)
                        )

        print("CSV import completed!")

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def delete_contact():
    name = input("Name to delete: ")

    conn = get_connection()
    if not conn:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM contacts WHERE name = %s",
                    (name,)
                )

        print("Contact deleted!")

    except Exception as error:
        print("Error:", error)

    finally:
        conn.close()


def main():
    while True:
        print("\n--- TSIS1 EXTENDED PHONEBOOK ---")
        print("1 - Add contact")
        print("2 - Show contacts")
        print("3 - Update phone")
        print("4 - Move contact to group")
        print("5 - Search contacts")
        print("6 - Filter by group")
        print("7 - Search by email")
        print("8 - Sort contacts")
        print("9 - Paginated navigation")
        print("10 - Export to JSON")
        print("11 - Import from JSON")
        print("12 - Import from CSV")
        print("13 - Delete contact")
        print("0 - Exit")

        choice = input("Choose: ")

        if choice == "1":
            add_contact()
        elif choice == "2":
            show_contacts()
        elif choice == "3":
            update_phone()
        elif choice == "4":
            move_to_group()
        elif choice == "5":
            search_contacts()
        elif choice == "6":
            filter_by_group()
        elif choice == "7":
            search_by_email()
        elif choice == "8":
            sort_contacts()
        elif choice == "9":
            paginated_navigation()
        elif choice == "10":
            export_to_json()
        elif choice == "11":
            import_from_json()
        elif choice == "12":
            import_from_csv()
        elif choice == "13":
            delete_contact()
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
