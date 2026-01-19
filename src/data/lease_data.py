"""
Medley Shopping Center - Complete Lease Database
Grand Opening: November 2026
Data extracted from executed lease documents - January 2026
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class RentScheduleEntry:
    period: str
    psf: float
    monthly: float
    notes: Optional[str] = None

@dataclass
class RentInfo:
    year1_psf: float
    year1_annual: float
    escalation: str
    escalation_rate: float
    escalation_period: int  # years

@dataclass
class CAMInfo:
    year1: Optional[float]
    type: str
    increases: Optional[str]

@dataclass
class TIInfo:
    psf: Optional[float]
    total: Optional[float]
    notes: Optional[str] = None

@dataclass
class CoTenancyInfo:
    type: str  # "Opening", "Operating", "Opening + Operating"
    threshold: str
    remedy: str
    termination: Optional[str]
    named_tenant: Optional[str]
    risk_level: str  # "high", "medium", "low"
    rent_at_risk: float
    notes: Optional[str] = None

@dataclass
class Lease:
    id: int
    tenant: str
    legal_entity: str
    suite: str
    sqft: int
    use: str
    category: str
    term: str
    term_months: int
    options: Optional[str]
    commence_date: str
    expire_date: str
    rent: RentInfo
    rent_schedule: List[RentScheduleEntry]
    cam: CAMInfo
    tax: Optional[float]
    insurance: Optional[float]
    recovery_note: Optional[str]
    ti: TIInfo
    co_tenancy: Optional[CoTenancyInfo]


LEASE_DATA: List[Lease] = [
    Lease(
        id=1, tenant="Trader Joe's", legal_entity="Trader Joe's East, Inc.", suite="1000", sqft=13524,
        use="Grocery Store", category="Anchor", term="10 years", term_months=120, options="Four 5-year extensions",
        commence_date="2026-11-01", expire_date="2036-10-31",
        rent=RentInfo(year1_psf=24.50, year1_annual=331338, escalation="10% every 5 years", escalation_rate=0.10, escalation_period=5),
        rent_schedule=[
            RentScheduleEntry(period="Years 1-5", psf=24.50, monthly=27611),
            RentScheduleEntry(period="Years 6-10", psf=26.95, monthly=30373),
        ],
        cam=CAMInfo(year1=8.00, type="Fixed CAM with CPI cap (4% max)", increases="CPI annually"),
        tax=None, insurance=None, recovery_note="Pro-rata insurance (10.8%)",
        ti=TIInfo(psf=None, total=None, notes="No TI - Landlord delivers shell"),
        co_tenancy=CoTenancyInfo(type="Opening", threshold="70,000 SF of other retailers open or scheduled to open", remedy="Defer opening OR 50% rent until satisfied", termination=None, named_tenant=None, risk_level="high", rent_at_risk=165669, notes="CRITICAL ANCHOR - triggers other co-tenancy"),
    ),
    Lease(
        id=2, tenant="Sephora", legal_entity="Sephora USA, Inc.", suite="1005", sqft=4721,
        use="Beauty Retail", category="Anchor", term="10 years", term_months=120, options="Two 5-year options",
        commence_date="2026-11-01", expire_date="2036-10-31",
        rent=RentInfo(year1_psf=42.00, year1_annual=198282, escalation="10% every 5 years", escalation_rate=0.10, escalation_period=5),
        rent_schedule=[
            RentScheduleEntry(period="Years 1-5", psf=42.00, monthly=16524),
            RentScheduleEntry(period="Years 6-10", psf=46.20, monthly=18176),
        ],
        cam=CAMInfo(year1=None, type="Modified Gross - CAM included", increases=None),
        tax=None, insurance=None, recovery_note="Gross lease - recoveries included",
        ti=TIInfo(psf=125.00, total=590125, notes="Major anchor buildout allowance"),
        co_tenancy=CoTenancyInfo(type="Opening + Operating", threshold="TJ's executed + 75% GLA; Operating: TJ's + 70% open", remedy="May defer; 50% rent if opens early", termination="Multiple triggers", named_tenant="Trader Joe's", risk_level="high", rent_at_risk=99141),
    ),
    Lease(
        id=3, tenant="Knuckies Hoagies", legal_entity="Knuckies Medley LLC", suite="1140", sqft=1200,
        use="Hoagie Shop", category="Restaurant", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=55.00, year1_annual=66000, escalation="3% annually", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Years 1-2", psf=55.00, monthly=5500),
            RentScheduleEntry(period="Year 5", psf=61.85, monthly=6185),
            RentScheduleEntry(period="Year 10", psf=71.71, monthly=7171),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="3% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=8.00, total=9600),
        co_tenancy=None,
    ),
    Lease(
        id=4, tenant="CRU Food & Wine Bar", legal_entity="Cru Medley, LLC", suite="2040", sqft=2100,
        use="Wine Bar & Restaurant", category="Restaurant", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=65.00, year1_annual=136500, escalation="10% every 5 years", escalation_rate=0.10, escalation_period=5),
        rent_schedule=[
            RentScheduleEntry(period="Years 1-5", psf=65.00, monthly=11375),
            RentScheduleEntry(period="Years 6-10", psf=71.50, monthly=12513),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="None specified"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=250.00, total=525000, notes="Significant buildout for wine bar"),
        co_tenancy=CoTenancyInfo(type="Opening", threshold="70% of shop space open or fixturing", remedy="50% Substitute Rent", termination="After 24 months, may terminate", named_tenant=None, risk_level="medium", rent_at_risk=68250),
    ),
    Lease(
        id=5, tenant="Five Daughters Bakery", legal_entity="Medley Five Daughters Bakery, LLC", suite="2110", sqft=806,
        use="Specialty Donuts", category="Food & Beverage", term="15 years", term_months=180, options=None,
        commence_date="2026-11-01", expire_date="2041-10-31",
        rent=RentInfo(year1_psf=69.00, year1_annual=55614, escalation="3% annually", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Year 1", psf=69.00, monthly=4635),
            RentScheduleEntry(period="Year 5", psf=77.66, monthly=5216),
            RentScheduleEntry(period="Year 10", psf=90.03, monthly=6047),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="5% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=8.00, total=6448),
        co_tenancy=CoTenancyInfo(type="Operating", threshold="After Year 3: <50% non-anchor GLA occupied", remedy="25% rent reduction (up to 12 mo)", termination="After 12 months remedy, may terminate", named_tenant=None, risk_level="low", rent_at_risk=13904),
    ),
    Lease(
        id=6, tenant="Playa Bowls", legal_entity="NP Johns Creek, LLC", suite="2450", sqft=1200,
        use="Acai & Smoothie Bowls", category="Food & Beverage", term="121 months", term_months=121, options="Two 5-year options",
        commence_date="2026-11-01", expire_date="2036-11-30",
        rent=RentInfo(year1_psf=58.00, year1_annual=69600, escalation="3% annually", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Months 1-24", psf=58.00, monthly=5800, notes="50% abatement Mo 1-3"),
            RentScheduleEntry(period="Months 49-60", psf=63.38, monthly=6338),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="5% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=8.00, total=9600),
        co_tenancy=None,
    ),
    Lease(
        id=7, tenant="Lily Sushi", legal_entity="Lily Sushi Medley LLC", suite="3040", sqft=2000,
        use="Sushi Restaurant", category="Restaurant", term="10 years", term_months=120, options=None,
        commence_date="2026-11-01", expire_date="2036-10-31",
        rent=RentInfo(year1_psf=62.50, year1_annual=125000, escalation="3% annually", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Year 1", psf=62.50, monthly=10417),
            RentScheduleEntry(period="Year 5", psf=70.35, monthly=11725),
            RentScheduleEntry(period="Year 10", psf=81.56, monthly=13593),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="Varies"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=8.00, total=16000),
        co_tenancy=None,
    ),
    Lease(
        id=8, tenant="26 Thai", legal_entity="26 Thai Medley LLC", suite="3100", sqft=4119,
        use="Thai Restaurant", category="Restaurant", term="121.5 months", term_months=122, options="Two 5-year options",
        commence_date="2026-11-01", expire_date="2036-12-15",
        rent=RentInfo(year1_psf=60.00, year1_annual=247140, escalation="2.5% annually", escalation_rate=0.025, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Months 1-12", psf=60.00, monthly=20595, notes="50% abatement Mo 1-3"),
            RentScheduleEntry(period="Months 49-60", psf=66.24, monthly=22737),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="4% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=8.00, total=32952),
        co_tenancy=None,
    ),
    Lease(
        id=9, tenant="Pause Studio", legal_entity="Pause Medley LLC", suite="3115", sqft=2800,
        use="Wellness & Meditation", category="Wellness", term="135 months", term_months=135, options=None,
        commence_date="2026-11-01", expire_date="2038-01-31",
        rent=RentInfo(year1_psf=55.00, year1_annual=154000, escalation="10% every 5 years", escalation_rate=0.10, escalation_period=5),
        rent_schedule=[
            RentScheduleEntry(period="Months 1-63", psf=55.00, monthly=12833),
            RentScheduleEntry(period="Months 64-123", psf=60.50, monthly=14117),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="3% annually"),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=60.00, total=168000),
        co_tenancy=CoTenancyInfo(type="Operating", threshold="After Mo 18: <65% Co-Tenancy Area occupied", remedy="50% Substitute Rent (up to 12 mo)", termination="After 12 months, may terminate", named_tenant=None, risk_level="medium", rent_at_risk=77000),
    ),
    Lease(
        id=10, tenant="High Country Outfitters", legal_entity="High Country, Inc.", suite="3120", sqft=4000,
        use="Outdoor Recreation Retail", category="Retail", term="10+ years", term_months=120, options="Two 5-year options",
        commence_date="2026-11-01", expire_date="2036-10-31",
        rent=RentInfo(year1_psf=50.00, year1_annual=200000, escalation="12.5% at Mo 64", escalation_rate=0.125, escalation_period=5),
        rent_schedule=[
            RentScheduleEntry(period="Months 1-3", psf=0.00, monthly=0, notes="FREE RENT"),
            RentScheduleEntry(period="Months 4-63", psf=50.00, monthly=16667),
            RentScheduleEntry(period="Months 64+", psf=56.25, monthly=18750),
        ],
        cam=CAMInfo(year1=17.00, type="Flat Rate NNN", increases="3% annually"),
        tax=1.00, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=25.00, total=100000),
        co_tenancy=CoTenancyInfo(type="Opening + Operating", threshold="65% GLA + TJ's; Operating: 60% GLA open", remedy="50% Substitute Rent", termination="After 12 months, Landlord forces election", named_tenant="Trader Joe's", risk_level="high", rent_at_risk=100000),
    ),
    Lease(
        id=11, tenant="Northern China Eatery", legal_entity="Golden Horse Medley, LLC", suite="3150", sqft=2500,
        use="Chinese Restaurant", category="Restaurant", term="121 months", term_months=121, options="Two 5-year options",
        commence_date="2026-11-01", expire_date="2036-11-30",
        rent=RentInfo(year1_psf=59.00, year1_annual=147500, escalation="3% annually", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Months 1-12", psf=59.00, monthly=12292, notes="50% abatement Mo 1-3"),
            RentScheduleEntry(period="Months 49-60", psf=66.40, monthly=13833),
        ],
        cam=CAMInfo(year1=19.00, type="Flat Rate NNN", increases="5% annually"),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=225.00, total=562500),
        co_tenancy=None,
    ),
    Lease(
        id=12, tenant="STIR", legal_entity="Stir Medley LLC", suite="3165", sqft=6000,
        use="Bar & Restaurant", category="Restaurant", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=55.00, year1_annual=330000, escalation="10% every 5 years", escalation_rate=0.10, escalation_period=5),
        rent_schedule=[
            RentScheduleEntry(period="Years 1-5", psf=55.00, monthly=27500),
            RentScheduleEntry(period="Years 6-10", psf=60.50, monthly=30250),
        ],
        cam=CAMInfo(year1=12.00, type="Flat Rate NNN", increases="2% annually"),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=90.00, total=540000),
        co_tenancy=None,
    ),
    Lease(
        id=13, tenant="Fado Irish Pub", legal_entity="Medley Irish Pub LLC", suite="3175", sqft=4200,
        use="Irish Pub & Restaurant", category="Restaurant", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=55.00, year1_annual=231000, escalation="2% annually", escalation_rate=0.02, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Years 1-2", psf=55.00, monthly=19250),
            RentScheduleEntry(period="Year 5", psf=58.36, monthly=20426),
            RentScheduleEntry(period="Year 10", psf=64.43, monthly=22551),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="3% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=200.00, total=840000, notes="Major pub buildout"),
        co_tenancy=CoTenancyInfo(type="Opening", threshold="60% of Co-Tenancy Area open", remedy="50% Substitute Rent", termination="After 18 months, Landlord forces election", named_tenant=None, risk_level="medium", rent_at_risk=115500),
    ),
    Lease(
        id=14, tenant="Cookie Fix", legal_entity="MRS Sweets Three, LLC", suite="4005", sqft=1000,
        use="Cookie & Dessert Shop", category="Food & Beverage", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=57.25, year1_annual=57250, escalation="3% annually", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Year 1", psf=57.25, monthly=4771),
            RentScheduleEntry(period="Year 5", psf=64.44, monthly=5370),
            RentScheduleEntry(period="Year 10", psf=74.70, monthly=6225),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="3% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=4.00, total=4000),
        co_tenancy=None,
    ),
    Lease(
        id=15, tenant="Sugarcoat Beauty", legal_entity="Sugarcoat Medley LLC", suite="4055", sqft=2500,
        use="Nail Salon & Beauty", category="Beauty/Spa", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=55.00, year1_annual=137500, escalation="3% annually", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Year 1", psf=55.00, monthly=11458),
            RentScheduleEntry(period="Year 5", psf=61.90, monthly=12896),
            RentScheduleEntry(period="Year 10", psf=71.76, monthly=14950),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="5% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=8.00, total=20000),
        co_tenancy=None,
    ),
    Lease(
        id=16, tenant="AYA Med Spa", legal_entity="Aesthetic Products, LLC", suite="4060", sqft=1500,
        use="Medical Spa", category="Medical/Spa", term="10 years", term_months=120, options="Two 5-year options",
        commence_date="2026-11-01", expire_date="2036-10-31",
        rent=RentInfo(year1_psf=62.50, year1_annual=93750, escalation="3% annually", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Year 1", psf=62.50, monthly=7813),
            RentScheduleEntry(period="Year 5", psf=70.35, monthly=8794),
            RentScheduleEntry(period="Year 10", psf=81.56, monthly=10195),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="5% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=118.00, total=177000),
        co_tenancy=None,
    ),
    Lease(
        id=17, tenant="Body20", legal_entity="Body20 Medley LLC", suite="4085", sqft=1300,
        use="EMS Fitness Studio", category="Fitness", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=55.00, year1_annual=71500, escalation="2.5% annually", escalation_rate=0.025, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Year 1", psf=55.00, monthly=5958),
            RentScheduleEntry(period="Year 5", psf=60.71, monthly=6577),
            RentScheduleEntry(period="Year 10", psf=68.69, monthly=7441),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="5% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=100.00, total=130000),
        co_tenancy=None,
    ),
    Lease(
        id=18, tenant="Basil Houze", legal_entity="Basil Houze LLC", suite="4112", sqft=991,
        use="Boutique Retail", category="Retail", term="7 years", term_months=84, options=None,
        commence_date="2026-11-01", expire_date="2033-10-31",
        rent=RentInfo(year1_psf=52.50, year1_annual=52028, escalation="3% annually", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Year 1", psf=52.50, monthly=4336),
            RentScheduleEntry(period="Year 3", psf=55.70, monthly=4600),
            RentScheduleEntry(period="Year 7", psf=62.69, monthly=5177),
        ],
        cam=CAMInfo(year1=19.00, type="Flat Rate NNN", increases="3% annually"),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=8.00, total=7928),
        co_tenancy=None,
    ),
    Lease(
        id=19, tenant="Clean Your Dirty Face", legal_entity="You Glow Girl LLC", suite="4115", sqft=878,
        use="Facial Spa", category="Beauty/Spa", term="123 months", term_months=123, options="Two 5-year options",
        commence_date="2026-11-01", expire_date="2037-01-31",
        rent=RentInfo(year1_psf=52.50, year1_annual=46095, escalation="2% annually", escalation_rate=0.02, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Months 1-12", psf=52.50, monthly=3841, notes="50% abatement Mo 1-3"),
            RentScheduleEntry(period="Months 49-60", psf=56.82, monthly=4157),
        ],
        cam=CAMInfo(year1=17.00, type="Flat Rate NNN", increases="3% annually"),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=140.00, total=122920),
        co_tenancy=CoTenancyInfo(type="Opening", threshold="70% of shop tenants open", remedy="50% rent abatement for 3 months", termination="None - rent reduction only", named_tenant=None, risk_level="low", rent_at_risk=11524),
    ),
    Lease(
        id=20, tenant="Burdlife", legal_entity="NDAD LLC", suite="4135", sqft=1200,
        use="Fried Chicken Restaurant", category="Restaurant", term="121 months", term_months=121, options="Two 5-year options",
        commence_date="2026-11-01", expire_date="2036-11-30",
        rent=RentInfo(year1_psf=60.00, year1_annual=72000, escalation="2.5% annually", escalation_rate=0.025, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Months 1-24", psf=60.00, monthly=6000, notes="50% abatement Mo 1-3"),
            RentScheduleEntry(period="Months 49-60", psf=64.62, monthly=6462),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="4% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=120.00, total=144000),
        co_tenancy=None,
    ),
    Lease(
        id=21, tenant="Petfolk", legal_entity="Petfolk Real Estate Holdings, LLC", suite="4138", sqft=1800,
        use="Veterinary & Pet Services", category="Pet Services", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=57.00, year1_annual=102600, escalation="2% annually", escalation_rate=0.02, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Year 1", psf=57.00, monthly=8550, notes="50% abatement Mo 1-6"),
            RentScheduleEntry(period="Year 5", psf=61.70, monthly=9255),
            RentScheduleEntry(period="Year 10", psf=68.12, monthly=10218),
        ],
        cam=CAMInfo(year1=17.00, type="Flat Rate NNN", increases="4% annually"),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=3.00, total=5400),
        co_tenancy=None,
    ),
    Lease(
        id=22, tenant="Kontour Medical Spa", legal_entity="Kontour Medley LLC", suite="4160", sqft=1500,
        use="Medical Spa & Aesthetics", category="Medical/Spa", term="124 months", term_months=124, options=None,
        commence_date="2026-11-01", expire_date="2037-02-28",
        rent=RentInfo(year1_psf=62.50, year1_annual=93750, escalation="3% annually", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Months 1-12", psf=62.50, monthly=7813, notes="50% abatement Mo 1-3"),
            RentScheduleEntry(period="Months 49-60", psf=70.35, monthly=8794),
        ],
        cam=CAMInfo(year1=17.00, type="Flat Rate NNN", increases=None),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=133.00, total=199500),
        co_tenancy=None,
    ),
    Lease(
        id=23, tenant="Drybar", legal_entity="Candibar LLC", suite="4165", sqft=1712,
        use="Blow Dry Bar", category="Beauty/Spa", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=42.00, year1_annual=71904, escalation="3% annually (after Y5)", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Years 1-5", psf=42.00, monthly=5992),
            RentScheduleEntry(period="Year 10", psf=48.70, monthly=6948),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="3% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=30.00, total=51360),
        co_tenancy=None,
    ),
    Lease(
        id=24, tenant="BODYROK", legal_entity="ADB Ventures LLC", suite="4180", sqft=2057,
        use="Pilates Reformer Studio", category="Fitness", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=60.00, year1_annual=123420, escalation="3% annually (after Y2)", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Years 1-2", psf=60.00, monthly=10285),
            RentScheduleEntry(period="Year 5", psf=65.56, monthly=11238),
            RentScheduleEntry(period="Year 10", psf=76.01, monthly=13029),
        ],
        cam=CAMInfo(year1=17.00, type="Flat Rate NNN", increases="5% annually"),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=150.00, total=308550),
        co_tenancy=None,
    ),
    Lease(
        id=25, tenant="Summit Coffee", legal_entity="Summit Coffee Medley LLC", suite="600", sqft=1167,
        use="Coffee Shop", category="Food & Beverage", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=50.00, year1_annual=58350, escalation="2.5% annually", escalation_rate=0.025, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Years 1-2", psf=50.00, monthly=4863),
            RentScheduleEntry(period="Year 5", psf=53.84, monthly=5236),
            RentScheduleEntry(period="Year 10", psf=60.92, monthly=5924),
        ],
        cam=CAMInfo(year1=15.00, type="Flat Rate NNN", increases="4% annually"),
        tax=4.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=8.00, total=9336),
        co_tenancy=None,
    ),
    Lease(
        id=26, tenant="Fogon & Lions", legal_entity="Fogon and Lions Medley, LLC", suite="6100", sqft=4707,
        use="Latin American Restaurant", category="Restaurant", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=50.00, year1_annual=235350, escalation="2-3% annually", escalation_rate=0.025, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Years 1-3", psf=50.00, monthly=19613),
            RentScheduleEntry(period="Year 5", psf=52.02, monthly=20405),
            RentScheduleEntry(period="Year 10", psf=60.32, monthly=23661),
        ],
        cam=CAMInfo(year1=17.00, type="Flat Rate NNN", increases="3% annually"),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=185.00, total=870795, notes="MAJOR restaurant buildout - highest TI"),
        co_tenancy=None,
    ),
    Lease(
        id=27, tenant="Rena's Italian", legal_entity="Rena's Medley LLC", suite="6110", sqft=4752,
        use="Italian Restaurant", category="Restaurant", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=60.00, year1_annual=285120, escalation="2% annually", escalation_rate=0.02, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Year 1", psf=60.00, monthly=23760),
            RentScheduleEntry(period="Year 5", psf=64.94, monthly=25716),
            RentScheduleEntry(period="Year 10", psf=71.70, monthly=28393),
        ],
        cam=CAMInfo(year1=17.00, type="Flat Rate NNN", increases="3% annually"),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=2.00, total=9504),
        co_tenancy=None,
    ),
    Lease(
        id=28, tenant="Amorino Gelato", legal_entity="TBC Johns Creek Gelato LLC", suite="6115", sqft=1200,
        use="Gelato & Italian Cafe", category="Food & Beverage", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=65.00, year1_annual=78000, escalation="3% annually", escalation_rate=0.03, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Year 1", psf=65.00, monthly=6500),
            RentScheduleEntry(period="Year 5", psf=73.16, monthly=7316),
            RentScheduleEntry(period="Year 10", psf=84.81, monthly=8481),
        ],
        cam=CAMInfo(year1=17.00, type="Flat Rate NNN", increases="5% annually"),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=8.00, total=9600),
        co_tenancy=None,
    ),
    Lease(
        id=29, tenant="Minnie Olivia Pizzeria", legal_entity="Minnie Olivia Pizzeria Medley, LLC", suite="6120", sqft=2366,
        use="Wood-Fired Pizza", category="Restaurant", term="20 years", term_months=240, options=None,
        commence_date="2026-11-01", expire_date="2046-10-31",
        rent=RentInfo(year1_psf=56.00, year1_annual=132496, escalation="2-3% annually", escalation_rate=0.025, escalation_period=1),
        rent_schedule=[
            RentScheduleEntry(period="Years 1-3", psf=56.00, monthly=11041),
            RentScheduleEntry(period="Year 5", psf=58.26, monthly=11487),
            RentScheduleEntry(period="Year 10", psf=67.54, monthly=13317),
        ],
        cam=CAMInfo(year1=17.00, type="Flat Rate NNN", increases="3% annually"),
        tax=2.25, insurance=0.75, recovery_note=None,
        ti=TIInfo(psf=8.00, total=18928),
        co_tenancy=None,
    ),
]


# Helper functions
def get_all_leases() -> List[Lease]:
    return LEASE_DATA

def get_lease_by_id(lease_id: int) -> Optional[Lease]:
    for lease in LEASE_DATA:
        if lease.id == lease_id:
            return lease
    return None

def get_lease_by_tenant(tenant_name: str) -> Optional[Lease]:
    for lease in LEASE_DATA:
        if lease.tenant.lower() == tenant_name.lower():
            return lease
    return None

def get_categories() -> List[str]:
    return sorted(list(set(lease.category for lease in LEASE_DATA)))

def get_tenants_by_category(category: str) -> List[Lease]:
    return [lease for lease in LEASE_DATA if lease.category == category]

def get_tenants_with_cotenancy() -> List[Lease]:
    return [lease for lease in LEASE_DATA if lease.co_tenancy is not None]

def calc_rent_for_year(lease: Lease, year: int) -> float:
    """Calculate rent for a given year based on escalation."""
    base = lease.rent.year1_annual
    rate = lease.rent.escalation_rate
    period = lease.rent.escalation_period

    if period == 1:
        return base * ((1 + rate) ** (year - 1))
    else:
        periods = (year - 1) // period
        return base * ((1 + rate) ** periods)

def get_summary_stats() -> Dict:
    """Calculate summary statistics for all leases."""
    total_sf = sum(lease.sqft for lease in LEASE_DATA)
    total_rent = sum(lease.rent.year1_annual for lease in LEASE_DATA)
    avg_psf = total_rent / total_sf if total_sf > 0 else 0
    cotenancy_count = len(get_tenants_with_cotenancy())
    total_ti = sum(lease.ti.total or 0 for lease in LEASE_DATA)

    return {
        "total_sf": total_sf,
        "total_rent": total_rent,
        "avg_psf": avg_psf,
        "cotenancy_count": cotenancy_count,
        "total_ti": total_ti,
        "tenant_count": len(LEASE_DATA),
    }
