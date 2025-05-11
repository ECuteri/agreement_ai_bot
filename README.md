# Company Information Retrieval API

A Flask API service that retrieves company information based on VAT ID from multiple sources.

## Features

- Retrieves company details from ufficiocamerale.it
- Retrieves company details from icribis.com
- Returns business name, address, and other company information
- Debug mode for directly fetching HTML sources

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

## API Endpoints

### Get Company Info from ufficiocamerale.it

```
POST /get_company_info
```

Request body:
```json
{
  "vat_id": "YOUR_VAT_ID"
}
```

### Get Company Info from icribis.com

```
POST /get_company_info_icribis
```

Request body:
```json
{
  "vat_id": "YOUR_VAT_ID"
}
```

### Debug Mode

To fetch HTML from a specific URL for debugging:

```json
{
  "debug_url": "https://example.com"
}
```

## Requirements

- Python 3.6+
- Flask
- Selenium
- BeautifulSoup4
- Chrome/Chromium browser (for Selenium WebDriver)