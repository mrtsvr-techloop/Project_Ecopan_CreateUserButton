import frappe

@frappe.whitelist()
def crea_utente(customer_name, customer_docname, user_email, user_password):
    try:
        # 1) controllo esistenza
        if frappe.db.exists("User", user_email):
            return {"success": False, "error": f"Utente {user_email} già esistente."}

        # 2) creo l'User
        user = frappe.get_doc({
            "doctype": "User",
            "email": user_email,
            "first_name": customer_name,
            "enabled": 1,
            "new_password": user_password
        }).insert(ignore_permissions=True)

        # 3) assegno il ruolo “Raven User”
        user.append("roles", {"role": "Raven User"})
        user.save(ignore_permissions=True)

        # 4) permesso sul record Ecopan Customer
        frappe.get_doc({
            "doctype": "User Permission",
            "user": user.name,
            "allow": "Ecopan Customer",
            "for_value": customer_docname
        }).insert(ignore_permissions=True)

        # 5) BLOCCO tutti i moduli tranne quelli consentiti
        allowed = {"Raven", "Raven Bot", "Raven AI", "Raven Messaging"}
        # prendo tutti i nomi di Module Def
        all_mods = [m.name for m in frappe.get_all("Module Def", fields=["name"])]
        # resetto eventuali blocchi e popolo solo per questo utente
        user.set("block_modules", [])
        for mod in all_mods:
            if mod not in allowed:
                user.append("block_modules", {"module": mod})
        user.save(ignore_permissions=True)

        return {"success": True, "user_email": user.email}

    except Exception:
        return {"success": False, "error": frappe.get_traceback()}
