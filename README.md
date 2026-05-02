# eand CX Solutions — MIS Request Management Portal

Internal web app for contact center teams to submit and manage MIS requests.

---

## Tech stack

| Layer     | Technology                      |
|-----------|---------------------------------|
| Frontend  | Streamlit                       |
| Backend   | Python 3.11+                    |
| Database  | Google Sheets (via `gspread`)   |
| Auth      | Session-based (`st.session_state`) |
| Charts    | Plotly                          |
| Hosting   | Streamlit Cloud (free tier)     |

---

## Folder structure

```
eand-mis-portal/
├── app.py                        # Entry point + sidebar navigation
├── auth.py                       # Login / session helpers
├── database.py                   # All Google Sheets read/write ops
├── utils.py                      # Request types, constants, formatters
├── requirements.txt
├── .gitignore
├── .streamlit/
│   ├── config.toml               # Theme + server config
│   └── secrets.toml.example      # Template — copy & fill in
└── pages/
    ├── dashboard.py              # Metrics + charts
    ├── submit.py                 # Submit new request
    ├── my_requests.py            # Staff: view own requests
    ├── all_requests.py           # MIS: view + update all requests
    └── users.py                  # MIS: add + manage users
```

---

## Local setup

### 1. Clone and install

```bash
git clone https://github.com/YOUR_ORG/eand-mis-portal.git
cd eand-mis-portal
pip install -r requirements.txt
```

### 2. Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet.
2. Note the **Spreadsheet ID** from the URL:  
   `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`

### 3. Create a Google Cloud service account

1. Go to [Google Cloud Console](https://console.cloud.google.com).
2. Create a new project (or use an existing one).
3. Enable **Google Sheets API** and **Google Drive API**.
4. Go to **IAM & Admin → Service Accounts** → Create service account.
5. Grant it the **Editor** role.
6. Create a **JSON key** and download it.
7. **Share your Google Sheet** with the service account email  
   (e.g. `mis-portal@your-project.iam.gserviceaccount.com`) — give it **Editor** access.

### 4. Configure secrets

Copy the template:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:
```toml
SPREADSHEET_ID = "your-sheet-id-here"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "your-sa@project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

> ⚠️ **Never commit** `secrets.toml` — it's in `.gitignore`.

### 5. Run locally

```bash
streamlit run app.py
```

Visit [http://localhost:8501](http://localhost:8501).  
Default admin login: `mis.admin` / `admin123`

---

## Deploy to Streamlit Cloud

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_ORG/eand-mis-portal.git
git push -u origin main
```

> Make sure `.gitignore` is in place so `secrets.toml` is **not** pushed.

### 2. Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **New app**.
3. Select your repository, branch (`main`), and set **Main file path** to `app.py`.
4. Click **Advanced settings → Secrets** and paste the full contents of your `secrets.toml`.
5. Click **Deploy**.

Streamlit Cloud will install dependencies from `requirements.txt` automatically.

---

## User roles

| Role  | Capabilities                                                    |
|-------|-----------------------------------------------------------------|
| Staff | Submit requests, view own requests and MIS responses            |
| MIS   | Everything above + all requests, dashboard, update/assign, users |

Default credentials (change after first login):

| Username      | Password   | Role  | Team       |
|---------------|------------|-------|------------|
| `mis.admin`   | `admin123` | MIS   | MIS        |

---

## Request types & dynamic fields

| Type                    | Extra fields                                              |
|-------------------------|-----------------------------------------------------------|
| Shift Swap              | Agent Name, Swap With, Original Date, New Date            |
| Schedule Change         | Agent Name, Effective Date, Reason                        |
| New Report Request      | Format (Excel/Sheets/PDF/Dashboard), Required By, Metrics |
| Agent Performance Issue | Agent Name, Agent ID, Incident Date                       |
| IT/System Issue         | System Affected, Users Affected                           |
| Other                   | Free text only                                            |

---

## Database (Google Sheets)

Three worksheets are auto-created on first run:

| Sheet       | Key columns                                                       |
|-------------|-------------------------------------------------------------------|
| Users       | username, password, fullName, team, status, role                  |
| Requests    | id, type, submittedBy, team, priority, subject, description, …    |
| ActivityLog | timestamp, user, action, detail                                   |

Request ID format: `REQ-YYYYMMDD-XXXX`  
Status flow: `Open → In Progress → Closed`

---

## Customisation tips

- **Email notifications:** add `sendgrid` to `requirements.txt` and call it inside `database.submit_request()`.
- **Password hashing:** replace plain-text passwords with `bcrypt` or `hashlib`.
- **Switch to SQLite:** replace all `gspread` calls in `database.py` with `sqlite3` — table structure stays identical.
- **Add more teams:** update the `TEAMS` list in `utils.py`.
