{% docs award_key %}
Surrogate key for an award, built in staging. Joins `fct_transactions` to `dim_awards`.
{% enddocs %}

{% docs award_id %}
Award identifier as reported by USAspending (PIID for contracts, FAIN for grants).
{% enddocs %}

{% docs transaction_key %}
Surrogate key for a single transaction (one obligation, modification, or de-obligation).
{% enddocs %}

{% docs recipient_uei %}
Unique Entity Identifier: the 12-character ID assigned to the recipient in SAM.gov.
{% enddocs %}

{% docs recipient_name %}
Recipient's name as reported to USAspending.
{% enddocs %}

{% docs awarding_agency %}
Top-tier federal agency that made the award, e.g. Department of Transportation.
{% enddocs %}

{% docs awarding_sub_agency %}
Sub-tier agency that made the award, e.g. Federal Highway Administration. Mapped to a sector by the `agency_sectors` seed.
{% enddocs %}

{% docs sector %}
Infrastructure sector of the awarding sub-agency (e.g. highways, transit, aviation), from the `agency_sectors` seed.
{% enddocs %}

{% docs award_type %}
`contracts` or `grants`, matching the award type used during ingestion.
{% enddocs %}

{% docs award_amount %}
Total award amount in USD as reported by USAspending at extraction time.
{% enddocs %}

{% docs start_date %}
Start date of the award's period of performance.
{% enddocs %}

{% docs state_code %}
Two-letter postal code of the place-of-performance state (SD, IA, NE, MN, or IL).
{% enddocs %}

{% docs state_name %}
Full state name, from the `states` seed.
{% enddocs %}

{% docs fiscal_year %}
Federal fiscal year (October 1 to September 30), named for the calendar year it ends in. FY2027 runs Oct 2026 to Sep 2027.
{% enddocs %}

{% docs latest_state_code %}
State code from the award's most recent extraction snapshot.
{% enddocs %}

{% docs latest_reported_fiscal_year %}
Most recent fiscal year in which this award appeared in the extracted data.
{% enddocs %}

{% docs action_date %}
Date the transaction was signed.
{% enddocs %}

{% docs modification_number %}
Modification number of the transaction. The original action has no modification number.
{% enddocs %}

{% docs transaction_amount %}
Amount obligated by this transaction in USD. Negative values are de-obligations.
{% enddocs %}

{% docs assistance_listing_number %}
Assistance Listing (formerly CFDA) number of the grant program, e.g. 20.205 (Highway Planning and Construction). Grants only.
{% enddocs %}

{% docs assistance_listing_title %}
Title of the Assistance Listing program, taken from the latest extraction.
{% enddocs %}

{% docs transactions %}
Number of transactions in the group.
{% enddocs %}

{% docs net_obligations %}
Sum of transaction amounts in USD: new obligations minus de-obligations.
{% enddocs %}

{% docs extracted_at %}
UTC timestamp when ingestion fetched the record from the USAspending API. Staging keeps only the latest snapshot.
{% enddocs %}

{% docs source_file %}
Name of the raw file the row was loaded from (`metadata$filename` during `COPY INTO`).
{% enddocs %}

{% docs loaded_at %}
Timestamp when the row was loaded into `RAW.USASPENDING`.
{% enddocs %}