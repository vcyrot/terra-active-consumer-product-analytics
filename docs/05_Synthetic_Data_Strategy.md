# Terra Active — Synthetic Data Strategy

## Objective

This document defines how Terra Active's synthetic data will be generated so that the final analytical environment behaves like a realistic consumer and product business rather than a collection of independent random tables.

The synthetic data should:

* Preserve the relational structure defined in `04_Data_Model.md`
* Reflect plausible consumer and retail behaviour
* Contain meaningful but imperfect relationships between variables
* Include time, seasonality and geography
* Support customer, product, digital, community, marketing and inventory analyses
* Include realistic data-quality issues for preprocessing exercises
* Remain fully fictional and independent from any real company

The goal is not to reproduce the exact economics of a real activewear brand.

The goal is to create a sufficiently realistic analytical environment in which business relationships must be discovered rather than being obvious from the raw data.

---

## 1. Simulation Period

The initial simulation period will cover three full years:

```text
2023-01-01 to 2025-12-31
```

A three-year period provides enough history for:

* Customer cohort analysis
* Repeat-purchase behaviour
* Customer lifetime value
* Seasonal demand
* Year-over-year comparisons
* Product launches
* Marketing campaigns
* Community events
* Weather-driven demand
* Inventory planning

The simulation should preserve historical information rather than generating only a final customer state.

---

## 2. Business Scale

The initial target scale should be large enough to support realistic SQL and Python analysis while remaining manageable on a personal computer.

Approximate target sizes:

| Dataset              |                         Initial Target |
| -------------------- | -------------------------------------: |
| Customers            |                                100,000 |
| Products             |                                150–250 |
| Orders               |                        200,000–300,000 |
| Order Items          |                        300,000–450,000 |
| Returns              |                          20,000–50,000 |
| Digital Events       |                            2–4 million |
| Community Events     |                                250–400 |
| Event Registrations  |                          20,000–50,000 |
| Challenges           |                                  20–40 |
| Campaigns            |                                 50–100 |
| Daily Inventory Rows | Dependent on product/location coverage |
| Weather Rows         |          One row per location per date |

These figures are initial targets and may be adjusted after performance testing.

The project should prioritise **quality and behavioural realism over raw volume**.

---

## 3. Geographic Markets

Terra Active operates across several European markets, but market size should not be evenly distributed.

Initial market structure:

| Market         | Relative Size | Typical Characteristics                     |
| -------------- | ------------- | ------------------------------------------- |
| United Kingdom | Large         | Strong running and lifestyle demand         |
| France         | Large         | Strong urban and outdoor customer base      |
| Germany        | Large         | Strong outdoor and technical demand         |
| Netherlands    | Medium        | Strong urban activewear and cycling culture |
| Spain          | Medium        | Warmer climate and seasonal apparel demand  |
| Italy          | Medium        | Strong lifestyle and fashion sensitivity    |
| Switzerland    | Smaller       | High-value technical and outdoor purchases  |

The final customer population should approximately reflect these relative market sizes.

Major cities may include:

* London
* Manchester
* Edinburgh
* Paris
* Lyon
* Annecy
* Berlin
* Munich
* Amsterdam
* Rotterdam
* Barcelona
* Madrid
* Milan
* Zurich

Locations will later support:

* Customer geography
* Community events
* Inventory
* Weather
* Market-level analysis

---

## 4. Customer Segments

The customer population will include five broad behavioural personas.

### Urban Runner

Typical tendencies:

* Lives in a major city
* Runs regularly
* Uses activewear for both exercise and everyday wear
* Higher-than-average purchase frequency
* Strong interest in new collections
* High mobile/app usage
* Relatively strong community-event participation
* Moderate to high accessory attachment

The segment should not guarantee these outcomes.

Some Urban Runners should remain occasional or one-time buyers.

---

### Outdoor Explorer

Typical tendencies:

* Interested in hiking, trail and outdoor activities
* Lower purchase frequency than Urban Runners
* Higher average basket value
* Greater interest in jackets, technical layers and backpacks
* Higher weather sensitivity
* Higher seasonal demand
* Strong participation in hiking and trail events

---

### Fitness Enthusiast

Typical tendencies:

* Interested in gym, Pilates and mobility
* Strong apparel demand
* Higher interest in leggings, sports bras and tops
* More responsive to new collections and social marketing
* Strong participation in Pilates or wellness events
* Moderate to high digital engagement

---

### Everyday Active

Typical tendencies:

* Recreationally active
* Lower purchase frequency
* More price-sensitive
* More responsive to promotions
* Lower Club and event engagement
* More likely to remain a one-time customer

---

### Performance Athlete

Typical tendencies:

* High sport intensity
* Greater interest in technical features
* Higher product knowledge
* Higher community engagement
* Higher loyalty probability
* More likely to attend advanced events and challenges
* Less driven by fashion trends than some other segments

---

## 5. Hidden Behavioural Traits

Customer behaviour should not depend only on visible segments.

Each synthetic customer may also receive internal behavioural traits that influence outcomes.

These traits are **generator variables** and do not necessarily appear in the final analytical dataset.

Potential latent traits:

```text
price_sensitivity
brand_affinity
fashion_affinity
sport_intensity
community_affinity
digital_engagement
promotion_sensitivity
return_propensity
novelty_seeking
```

These variables create individual variation within customer segments.

For example:

```text
Urban Runner
+
High fashion affinity
+
High digital engagement
+
Low price sensitivity
```

may become a frequent purchaser of new collections.

Another Urban Runner with:

```text
Low brand affinity
+
High price sensitivity
```

may purchase only during promotions.

This prevents the final dataset from becoming deterministically segmented.

---

## 6. Customer Lifecycle

Customers should be generated over time rather than all existing on the first day of the simulation.

A simplified customer lifecycle may include:

```text
Prospect
    ↓
Account Signup
    ↓
First Purchase
    ↓
Repeat Customer
    ↓
Club Member
    ↓
Event / Challenge Participant
    ↓
Highly Engaged Customer
```

Not every customer will move through every stage.

Some may:

* Sign up but never purchase
* Purchase once and disappear
* Join the Club before purchasing
* Attend events without becoming high spenders
* Become loyal customers without participating in community activities

This creates realistic heterogeneity.

---

## 7. Customer Acquisition

New customers should enter the ecosystem through different acquisition channels.

Potential channels:

* Organic Search
* Direct
* Instagram
* TikTok
* Paid Search
* Email Referral
* Friend Referral
* Community Event
* Influencer
* Store / Offline

Acquisition channels should differ in:

* Customer acquisition cost
* Customer volume
* Typical customer profile
* Purchase conversion
* Long-term retention

Example hidden relationship:

> Paid social may acquire customers cheaply and at high volume, while organic and referral customers may have stronger long-term retention.

This should be probabilistic rather than universal.

---

## 8. Product Catalogue Strategy

The product catalogue should contain approximately 150–250 products across apparel and accessories.

### Apparel

Potential subcategories:

* Running jackets
* Waterproof shells
* Fleeces
* T-shirts
* Long sleeves
* Base layers
* Shorts
* Leggings
* Pants
* Joggers
* Sports bras

### Accessories

Potential subcategories:

* Running vests
* Backpacks
* Caps
* Beanies
* Sunglasses
* Socks
* Gloves
* Water bottles
* Hydration flasks

Products should vary by:

* Price
* Cost
* Margin
* Sport positioning
* Lifestyle vs technical positioning
* Colour
* Gender positioning
* Collection
* Launch date
* Sustainability attributes
* Waterproofing
* Insulation

---

## 9. Product Pricing

Prices should follow realistic category-specific ranges rather than one global random distribution.

Illustrative ranges:

| Product Type      | Approximate Retail Price Range |
| ----------------- | -----------------------------: |
| T-Shirts          |                        €40–€80 |
| Sports Bras       |                        €50–€90 |
| Shorts            |                       €60–€110 |
| Leggings          |                       €80–€140 |
| Pants / Joggers   |                       €90–€160 |
| Fleeces           |                      €120–€220 |
| Jackets           |                      €150–€350 |
| Waterproof Shells |                      €220–€450 |
| Socks             |                        €15–€30 |
| Caps / Beanies    |                        €25–€50 |
| Sunglasses        |                       €80–€180 |
| Running Vests     |                       €90–€180 |
| Backpacks         |                      €100–€250 |

Unit cost should vary by product type and technical complexity.

Margin should therefore differ across products.

A high-revenue product should not automatically be the highest-margin product.

---

## 10. Product Demand Behaviour

Demand should depend on several factors.

Potential drivers:

* Customer segment
* Sport preference
* Product category
* Price
* Discount
* Collection launch
* Season
* Weather
* Marketing campaign
* Product popularity
* Stock availability
* Previous customer purchases

Examples:

* Urban Runners are more likely to purchase versatile jackets, tops and accessories.
* Outdoor Explorers have greater interest in waterproof products and backpacks.
* Fitness Enthusiasts are more likely to purchase leggings, sports bras and lightweight tops.
* Performance Athletes are more likely to purchase highly technical products.
* Everyday Active customers are more promotion-sensitive.

These relationships should include overlap and randomness.

---

## 11. Order Behaviour

Order frequency should vary by customer.

Potential drivers:

```text
customer_segment
brand_affinity
customer_tenure
price_sensitivity
club_membership
digital_engagement
season
marketing exposure
previous purchases
```

The distribution should be right-skewed.

Expected pattern:

* Many customers make only one purchase
* A smaller group makes two to four purchases
* A small group of highly engaged customers makes many purchases

Basket sizes should also vary.

Typical order:

* 1–3 items

Occasional larger baskets:

* 4+ items

Accessory cross-selling should be intentionally embedded.

Examples:

```text
Jacket + Cap
Jacket + Gloves
Shorts + Socks
Leggings + Socks
Running Vest + Hydration Flask
```

These relationships should increase the probability of co-purchase without making them automatic.

---

## 12. Promotions and Discounting

Not all customers should respond equally to discounts.

Discount behaviour should depend partly on:

* Price sensitivity
* Acquisition source
* Customer segment
* Product lifecycle
* Campaigns
* Seasonality

Potential discount levels:

```text
0%
10%
15%
20%
25%
30%
```

Heavy discounting should be relatively uncommon for a premium brand.

The dataset should allow analysis of:

* Volume uplift
* Margin reduction
* Customer discount dependency
* Post-promotion purchasing behaviour

---

## 13. Returns Behaviour

Returns should vary by category and customer.

Potential drivers:

* Product category
* Fit-sensitive products
* Discounting
* Customer return propensity
* Purchase channel
* Basket size
* Product quality
* Delivery issues

Illustrative tendencies:

* Leggings and sports bras may have higher fit-related return rates
* Accessories may have lower return rates
* Large promotional baskets may have higher return probability
* Some customers may systematically return more than others

Return reasons should be generated probabilistically.

Potential reasons:

* Size / Fit
* Changed Mind
* Product Appearance
* Quality Issue
* Incorrect Item
* Damaged
* Delivery Issue

---

## 14. Digital Behaviour

Digital activity should be event-based.

A typical customer journey may contain:

```text
session_start
page_view
view_product
add_to_favourites
add_to_cart
begin_checkout
purchase
```

Many sessions should not result in purchases.

Customer digital behaviour should depend on:

* Digital engagement
* Device
* Customer status
* Acquisition source
* Product interest
* Purchase intent

Potential friction should be intentionally embedded.

Example:

> Mobile checkout may have a slightly lower completion rate than desktop during part of the simulation.

This creates a future Product Analytics investigation.

---

## 15. Purchase Funnel Behaviour

The digital purchase funnel should include realistic drop-off.

Illustrative structure:

```text
Session
    ↓
Product View
    ↓
Add to Cart
    ↓
Begin Checkout
    ↓
Purchase
```

Conversion probabilities should differ by:

* Device
* New vs returning customer
* Customer segment
* Traffic source
* Product category
* Promotion exposure

The funnel should not use fixed conversion rates for every customer.

---

## 16. Terra Active Club

Club membership probability should depend on engagement.

Potential drivers:

* Repeat purchases
* Event interest
* Brand affinity
* Digital engagement
* Referral exposure

Club members may have higher observed purchasing and retention.

However, this should include **selection bias**.

Customers with high brand affinity should already be more likely to:

* Join the Club
* Purchase repeatedly
* Attend events

A smaller additional post-membership effect may also be simulated.

This allows later analysis to distinguish:

```text
Customers are loyal because they joined the Club
```

from:

```text
Loyal customers are more likely to join the Club
```

---

## 17. Community Events

Events should occur across major European cities.

Potential types:

* Community Run
* Long Run
* Trail Run
* Hiking Day
* Hiking Weekend
* Pilates
* Mobility Session
* Seasonal Community Event

Each event should contain:

* Location
* Capacity
* Date
* Difficulty
* Price
* Club restrictions
* Weather sensitivity

Event participation probability should depend on:

* Distance from customer location
* Preferred sport
* Club membership
* Community affinity
* Event difficulty
* Price
* Prior participation

---

## 18. Event Attendance

Registration should not guarantee attendance.

Attendance may depend on:

* Weather
* Event type
* Registration lead time
* Previous attendance
* Price
* Customer engagement

Examples:

* Heavy rain may reduce attendance at city runs
* Rain may have less impact on highly committed trail runners
* Pilates events may be less weather-sensitive

Event attendees may display stronger post-event engagement, but attendees should also already differ from non-attendees before the event.

---

## 19. Challenges

Terra Active challenges should encourage recurring digital and community engagement.

Potential examples:

* 30-Day Movement Challenge
* Autumn Running Challenge
* Summer Hiking Challenge
* Winter Outdoor Challenge
* Mobility Month

Challenge participation should depend on:

* Club membership
* Sport preference
* Digital engagement
* Community affinity

Completion probability should depend on:

* Challenge difficulty
* Customer engagement
* Prior challenge participation

---

## 20. Marketing Campaigns

Marketing campaigns should vary by:

* Channel
* Target segment
* Product collection
* Objective
* Budget
* Duration

Potential campaign types:

* Acquisition
* New Collection
* Product Promotion
* Event Promotion
* Club Engagement
* Retention

Campaign outcomes should vary.

Some campaigns may:

* Generate high customer volume but low long-term value
* Generate fewer customers with stronger retention
* Produce strong revenue but weak margin
* Drive event registrations rather than purchases

This allows meaningful marketing analysis later.

---

## 21. Seasonality

The business should contain strong but imperfect seasonality.

Potential patterns:

### Winter

Higher demand for:

* Jackets
* Waterproof shells
* Fleeces
* Gloves
* Beanies

### Spring

Higher demand for:

* Running apparel
* Lightweight jackets
* Shorts

### Summer

Higher demand for:

* T-shirts
* Shorts
* Sunglasses
* Caps
* Hydration accessories

### Autumn

Higher demand for:

* Layers
* Running jackets
* Trail-oriented products

Seasonality should differ across countries because climate differs across Europe.

---

## 22. Weather Effects

Weather will be sourced from historical data where possible.

Weather may influence:

### Product Demand

Examples:

* Rain increases waterproof-product demand
* Cold temperatures increase insulation and layering demand
* Sunny conditions increase sunglasses and cap demand
* Hot conditions increase shorts and lightweight-top demand

### Community Events

Examples:

* Rain reduces attendance for some outdoor events
* Severe weather increases cancellations
* Mild weather increases registrations for outdoor activities

Weather effects should interact with geography and seasonality.

---

## 23. Inventory Behaviour

Inventory should respond to expected demand but remain imperfect.

Stock levels should depend on:

* Historical demand
* Season
* Product popularity
* Collection launch
* Replenishment timing

The simulation should deliberately create some stockouts.

Stockouts may occur because of:

* Unexpected demand
* Weather spikes
* Campaign success
* Product launches
* Delayed replenishment

This allows estimation of lost sales and demand-planning analysis.

---

## 24. Hidden Ground Truth Relationships

The following relationships may be intentionally embedded in the synthetic data.

They should **not be directly exposed in the final analytical dataset**.

Examples:

1. Urban Runners have moderately higher purchase frequency.
2. Some accessories exhibit strong cross-sell relationships with selected apparel categories.
3. Fit-sensitive apparel categories have higher return rates.
4. Highly engaged customers are more likely to join Terra Active Club.
5. Club membership has a smaller additional positive effect on engagement.
6. Event attendees are more engaged even before attending.
7. Event attendance creates a small additional increase in subsequent engagement.
8. Referral and organic customers have stronger retention than some paid-social customers.
9. Mobile checkout contains a subtle period-specific friction.
10. Rain increases waterproof-product demand.
11. Cold weather increases demand for insulated products.
12. Successful campaigns can create temporary stockouts.
13. Discount-sensitive customers have lower average margins.
14. Newer customers mechanically have lower observed historical CLV.
15. High app engagement is correlated with purchasing but does not guarantee conversion.

These hidden relationships create analytical problems that can later be investigated using SQL, Python and statistical methods.

---

## 25. Noise and Imperfect Relationships

No simulated relationship should be deterministic.

For example:

```text
Urban Runner ≠ guaranteed high-value customer
Club Member ≠ guaranteed repeat customer
Event Attendee ≠ guaranteed purchaser
Rain ≠ guaranteed jacket purchase
```

Behaviour should always contain randomness, overlapping preferences and exceptions.

The objective is to create statistical tendencies rather than pre-written conclusions.

---

## 26. Data Quality Problems

The raw synthetic environment should intentionally contain a controlled amount of imperfect data.

Potential issues:

* Duplicate digital events
* Missing campaign attribution
* Missing customer IDs for anonymous sessions
* Inconsistent city names
* Missing product attributes
* Malformed timestamps
* Duplicate records
* Missing event feedback
* Rare impossible values
* Delayed records
* Inconsistent categorical casing
* Unexpected null values

These issues will be generated deliberately and documented.

The preprocessing pipeline will then be responsible for:

* Identifying
* Cleaning
* Validating
* Logging
* Reporting

the issues.

---

## 27. Data Generation Layers

The generation process should follow dependencies.

### Layer 1 — Reference Data

Generate first:

```text
locations
products
campaigns
challenges
community_events
```

These tables do not require existing customer transactions.

### Layer 2 — Customers

Generate:

```text
customers
customer_acquisition
club_memberships
```

### Layer 3 — Commercial Behaviour

Generate:

```text
orders
order_items
returns
```

### Layer 4 — Digital Behaviour

Generate:

```text
digital_events
```

Digital events should be consistent with generated purchases where relevant.

For example, many online purchases should have corresponding checkout and purchase events.

### Layer 5 — Community Behaviour

Generate:

```text
event_registrations
challenge_participation
```

### Layer 6 — Operations & External Data

Generate or source:

```text
weather_daily
inventory_daily
```

Inventory should interact with product demand and stock availability.

---

## 28. Reproducibility

Synthetic generation should be reproducible.

A fixed random seed should be stored centrally.

Example:

```python
RANDOM_SEED = 42
```

The generator should allow scale and configuration to be changed without rewriting the generation logic.

Potential configurable parameters include:

```text
simulation_start_date
simulation_end_date
number_of_customers
number_of_products
random_seed
market_weights
segment_weights
```

---

## 29. Validation Strategy

Each generated table should be validated before downstream tables are created.

Examples:

### Customers

Check:

* Unique customer IDs
* Age distribution
* Country distribution
* Segment distribution
* Signup-date distribution

### Products

Check:

* Unique product IDs
* Price ranges
* Margin ranges
* Category distribution
* Launch dates

### Orders

Check:

* Order-frequency distribution
* Basket-size distribution
* Revenue distribution
* Customer repeat behaviour

### Events

Check:

* Registration rates
* Attendance rates
* Capacity usage

The generator should not be considered complete until generated distributions are reviewed.

---

## 30. Transparency

The project must clearly state that:

> Terra Active is a fictional company and all commercial, customer and operational data generated for the project are synthetic.

External sources may be used to inform:

* Weather observations
* Event-taxonomy design
* Ecommerce event structures
* Broad distribution assumptions

However, no generated metric should be presented as representing the actual performance of any real activewear company.

---

## 31. Next Steps

The next implementation phase will build the database incrementally.

Recommended generation order:

1. Create project configuration
2. Generate `locations`
3. Generate `products`
4. Validate the product catalogue
5. Generate `customers`
6. Validate customer distributions
7. Generate customer acquisition
8. Generate orders and order items
9. Validate commercial behaviour
10. Add returns
11. Add digital events
12. Add Club and community behaviour
13. Add campaigns and challenges
14. Integrate historical weather
15. Generate inventory behaviour
16. Introduce controlled data-quality issues
17. Build the preprocessing pipeline
18. Load the clean relational dataset into SQL
