# Multi-source collection

This module keeps existing Ctrip data in `T_Core_attractions`, stores every new platform record in
`T_Raw_Platform_Spot`, then merges each normalized spot into `T_Core_attractions`.

## 1. Prepare database

```powershell
python -m main.multisource.run_collect init-db
```

This creates `T_Raw_Platform_Spot` and adds source columns to `T_Core_attractions`.

## 2. Collect AMap POI data

Apply a WebService API key from AMap Open Platform, then run:

```powershell
$env:AMAP_KEY="your-key"
python -m main.multisource.run_collect amap --keyword "景点" --city "武汉" --max-page 5
```

## 3. Import another platform by CSV

CSV headers can use the same names as existing fields:

```text
source_id,source_url,poiname,commentscore,commentcount,heatscore,jiage,districtname,zonename,imgurl
```

Then import:

```powershell
python -m main.multisource.run_collect csv --platform qunar --path D:\data\qunar_spots.csv
python -m main.multisource.run_collect csv --platform mafengwo --path D:\data\mafengwo_spots.csv
```

## 4. Public page collection

Only use this for public pages that robots.txt allows. Do not bypass login, captcha, rate limits,
or anti-bot systems.

Prepare an XPath mapping JSON:

```json
{
  "poiname": "//h1/text()",
  "commentscore": "//*[contains(@class, 'score')]/text()",
  "districtname": "//*[contains(@class, 'city')]/text()"
}
```

Run:

```powershell
python -m main.multisource.run_collect public-page --platform example --mapping D:\data\xpath.json --url "https://example.com/spot/1"
```

