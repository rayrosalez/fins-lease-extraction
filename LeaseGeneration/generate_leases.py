#!/usr/bin/env python3
"""
Synthetic Commercial Lease Agreement Generator
Generates realistic, multi-page PDF lease agreements with all required fields
"""

import random
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
import os


# Real US addresses database
US_ADDRESSES = [
    {"street": "350 Fifth Avenue", "city": "New York", "state": "NY", "zip": "10118", "country": "United States"},
    {"street": "1600 Pennsylvania Avenue NW", "city": "Washington", "state": "DC", "zip": "20500", "country": "United States"},
    {"street": "233 South Wacker Drive", "city": "Chicago", "state": "IL", "zip": "60606", "country": "United States"},
    {"street": "1 Market Street", "city": "San Francisco", "state": "CA", "zip": "94105", "country": "United States"},
    {"street": "1801 California Street", "city": "Denver", "state": "CO", "zip": "80202", "country": "United States"},
    {"street": "500 Boylston Street", "city": "Boston", "state": "MA", "zip": "02116", "country": "United States"},
    {"street": "1100 Congress Avenue", "city": "Austin", "state": "TX", "zip": "78701", "country": "United States"},
    {"street": "1201 Third Avenue", "city": "Seattle", "state": "WA", "zip": "98101", "country": "United States"},
    {"street": "999 Peachtree Street NE", "city": "Atlanta", "state": "GA", "zip": "30309", "country": "United States"},
    {"street": "200 East Randolph Street", "city": "Chicago", "state": "IL", "zip": "60601", "country": "United States"},
    {"street": "1901 Main Street", "city": "Dallas", "state": "TX", "zip": "75201", "country": "United States"},
    {"street": "1633 Broadway", "city": "New York", "state": "NY", "zip": "10019", "country": "United States"},
    {"street": "601 California Street", "city": "San Francisco", "state": "CA", "zip": "94108", "country": "United States"},
    {"street": "1750 Pennsylvania Avenue NW", "city": "Washington", "state": "DC", "zip": "20006", "country": "United States"},
    {"street": "100 Crescent Court", "city": "Dallas", "state": "TX", "zip": "75201", "country": "United States"},
    {"street": "1000 Wilshire Boulevard", "city": "Los Angeles", "state": "CA", "zip": "90017", "country": "United States"},
    {"street": "1455 Market Street", "city": "San Francisco", "state": "CA", "zip": "94103", "country": "United States"},
    {"street": "2100 Ross Avenue", "city": "Dallas", "state": "TX", "zip": "75201", "country": "United States"},
    {"street": "1271 Avenue of the Americas", "city": "New York", "state": "NY", "zip": "10020", "country": "United States"},
    {"street": "800 North Glebe Road", "city": "Arlington", "state": "VA", "zip": "22203", "country": "United States"},
]

TENANT_NAMES = [
    "Acme Corporation", "TechFlow Solutions Inc.", "Global Innovations LLC",
    "Premier Consulting Group", "Silverstone Enterprises", "Phoenix Trading Company",
    "Meridian Financial Services", "Cascade Technologies Inc.", "Summit Retail Group",
    "Horizon Healthcare Partners", "Vertex Manufacturing Co.", "Atlas Logistics LLC",
    "Quantum Research Labs", "Northstar Pharmaceuticals", "Redwood Capital Partners",
    "Evergreen Media Group", "Stratosphere Aerospace", "Pinnacle Law Firm LLP",
    "Oceanic Systems Inc.", "Cornerstone Architecture"
]

LANDLORD_NAMES = [
    "Metropolitan Real Estate Holdings LLC", "Urban Properties Group Inc.",
    "Skyline Investment Partners", "Prestige Commercial Realty LLC",
    "Cityscape Development Corporation", "Landmark Property Management Inc.",
    "Summit Realty Holdings LLC", "Gateway Commercial Properties",
    "Premier Building Group LLC", "Tower Property Ventures Inc."
]

LANDLORD_ADDRESSES = [
    {"street": "1500 Broadway", "city": "New York", "state": "NY", "zip": "10036"},
    {"street": "2001 Market Street", "city": "Philadelphia", "state": "PA", "zip": "19103"},
    {"street": "1200 Smith Street", "city": "Houston", "state": "TX", "zip": "77002"},
    {"street": "100 Pine Street", "city": "San Francisco", "state": "CA", "zip": "94111"},
    {"street": "300 South Grand Avenue", "city": "Los Angeles", "state": "CA", "zip": "90071"},
]

INDUSTRY_SECTORS = [
    "Technology", "Financial Services", "Healthcare", "Legal Services",
    "Retail", "Consulting", "Manufacturing", "Media & Entertainment",
    "Pharmaceuticals", "Telecommunications", "Aerospace", "Real Estate Services"
]

LEASE_TYPES = [
    "Triple Net (NNN)", "Modified Gross", "Full Service Gross", "Absolute Net"
]

SUITE_NUMBERS = [
    "Suite 100", "Suite 250", "Suite 305", "Suite 420", "Suite 550", "Suite 610",
    "Suite 750", "Suite 800", "Suite 900", "Suite 1200", "Suite 1450", "Suite 1600",
    "Penthouse A", "Floor 10", "Suite 2500"
]


class LeaseGenerator:
    """Generates realistic commercial lease agreements as PDFs"""
    
    def __init__(self, output_dir="generated_leases"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for the document"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='LeaseTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='LeaseBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
        
        # Small print style
        self.styles.add(ParagraphStyle(
            name='SmallPrint',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=11,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
    
    def generate_lease_data(self):
        """Generate random but realistic lease data"""
        # Select random addresses
        property_addr = random.choice(US_ADDRESSES)
        landlord_addr = random.choice(LANDLORD_ADDRESSES)
        
        # Generate dates
        start_date = datetime.now() + timedelta(days=random.randint(-730, 90))
        term_months = random.choice([36, 48, 60, 84, 120])
        end_date = start_date + timedelta(days=term_months * 30)
        
        # Generate financial terms
        square_feet = random.randint(2000, 25000)
        base_rent_psf = round(random.uniform(25.0, 85.0), 2)
        annual_base_rent = int(square_feet * base_rent_psf)
        monthly_base_rent = round(annual_base_rent / 12, 2)
        
        # Additional financial details
        escalation_pct = random.choice([2, 3, 3, 4])  # More weight on 3%
        additional_rent_estimate = round(square_feet * random.uniform(8.0, 15.0), 2)
        pro_rata_share = round(square_feet / random.randint(50000, 150000), 4)
        security_deposit = monthly_base_rent * random.choice([1, 2, 3])
        
        # Renewal and termination options
        renewal_options = random.choice([
            "Two (2) five-year renewal options",
            "One (1) five-year renewal option",
            "Three (3) three-year renewal options",
            "One (1) ten-year renewal option"
        ])
        renewal_notice_days = random.choice([90, 120, 180, 270, 360])
        
        termination_rights = random.choice([
            "Tenant may terminate after 36 months with 6 months notice and payment of unamortized tenant improvements",
            "Early termination not permitted except in case of building sale or condemnation",
            "Tenant may terminate with 12 months notice and payment of termination fee equal to 6 months base rent"
        ])
        
        guarantor = random.choice([
            "Personal guaranty by John Smith, CEO",
            "Corporate parent guaranty by " + random.choice(TENANT_NAMES),
            "Letter of credit in the amount of $" + f"{int(security_deposit * 2):,}",
            "No guaranty required"
        ])
        
        return {
            # Landlord
            "landlord_name": random.choice(LANDLORD_NAMES),
            "landlord_address": f"{landlord_addr['street']}, {landlord_addr['city']}, {landlord_addr['state']} {landlord_addr['zip']}",
            
            # Tenant
            "tenant_name": random.choice(TENANT_NAMES),
            "tenant_address": f"{property_addr['street']}, {property_addr['city']}, {property_addr['state']} {property_addr['zip']}",
            "industry_sector": random.choice(INDUSTRY_SECTORS),
            
            # Property Location
            "property_street": property_addr['street'],
            "property_city": property_addr['city'],
            "property_state": property_addr['state'],
            "property_zip": property_addr['zip'],
            "property_country": property_addr['country'],
            "property_full_address": f"{property_addr['street']}, {property_addr['city']}, {property_addr['state']} {property_addr['zip']}, {property_addr['country']}",
            
            # Lease Details
            "suite_number": random.choice(SUITE_NUMBERS),
            "lease_type": random.choice(LEASE_TYPES),
            "commencement_date": start_date,
            "expiration_date": end_date,
            "term_months": term_months,
            "rentable_square_feet": square_feet,
            
            # Financial Terms
            "annual_base_rent": annual_base_rent,
            "monthly_base_rent": monthly_base_rent,
            "base_rent_psf": base_rent_psf,
            "annual_escalation_pct": escalation_pct,
            "additional_rent_estimate": additional_rent_estimate,
            "pro_rata_share": pro_rata_share,
            "security_deposit": int(security_deposit),
            
            # Risk and Options
            "renewal_options": renewal_options,
            "renewal_notice_days": renewal_notice_days,
            "termination_rights": termination_rights,
            "guarantor": guarantor,
        }
    
    def create_lease_pdf(self, lease_data, filename=None):
        """Generate a complete multi-page lease PDF"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lease_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Page 1: Title and Parties
        story.append(Paragraph("COMMERCIAL LEASE AGREEMENT", self.styles['LeaseTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Basic information table
        basic_info = [
            ["<b>Date of Execution:</b>", datetime.now().strftime("%B %d, %Y")],
            ["<b>Property Address:</b>", lease_data['property_full_address']],
            ["<b>Suite/Unit:</b>", lease_data['suite_number']],
        ]
        
        t = Table(basic_info, colWidths=[2*inch, 4.5*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))
        
        # Section 1: PARTIES
        story.append(Paragraph("ARTICLE I: PARTIES TO THE LEASE", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"<b>1.1 LANDLORD:</b> {lease_data['landlord_name']}, a limited liability company organized "
            f"under the laws of the State of Delaware, with a principal place of business at "
            f"{lease_data['landlord_address']} (hereinafter referred to as \"<b>Landlord</b>\").",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>1.2 TENANT:</b> {lease_data['tenant_name']}, a corporation engaged in the "
            f"{lease_data['industry_sector']} industry, with an address at "
            f"{lease_data['tenant_address']} (hereinafter referred to as \"<b>Tenant</b>\").",
            self.styles['LeaseBody']
        ))
        
        # Section 2: PREMISES
        story.append(Paragraph("ARTICLE II: DEMISED PREMISES", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"<b>2.1 PREMISES DESCRIPTION:</b> Landlord hereby leases to Tenant, and Tenant hereby "
            f"leases from Landlord, those certain premises known as {lease_data['suite_number']}, located at "
            f"{lease_data['property_street']}, {lease_data['property_city']}, "
            f"{lease_data['property_state']} {lease_data['property_zip']}, {lease_data['property_country']} "
            f"(the \"<b>Premises</b>\"). The Premises shall include all improvements, fixtures, and "
            f"appurtenances located therein.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>2.2 RENTABLE SQUARE FEET:</b> The Premises contain approximately "
            f"{lease_data['rentable_square_feet']:,} rentable square feet (RSF), as measured in accordance "
            f"with the Building Owners and Managers Association (BOMA) standards.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>2.3 LEASE TYPE:</b> This lease shall be classified as a <b>{lease_data['lease_type']}</b> lease. "
            f"Tenant acknowledges and agrees to the obligations and responsibilities associated with this lease structure.",
            self.styles['LeaseBody']
        ))
        
        # Section 3: TERM
        story.append(Paragraph("ARTICLE III: LEASE TERM", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"<b>3.1 COMMENCEMENT DATE:</b> The term of this Lease shall commence on "
            f"<b>{lease_data['commencement_date'].strftime('%B %d, %Y')}</b> (the \"<b>Commencement Date</b>\").",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>3.2 EXPIRATION DATE:</b> Unless sooner terminated as provided herein, this Lease shall "
            f"expire on <b>{lease_data['expiration_date'].strftime('%B %d, %Y')}</b> (the \"<b>Expiration Date</b>\"), "
            f"at 11:59 p.m. local time.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>3.3 TERM LENGTH:</b> The initial term of this Lease shall be <b>{lease_data['term_months']} months</b> "
            f"({lease_data['term_months']//12} years).",
            self.styles['LeaseBody']
        ))
        
        story.append(PageBreak())
        
        # Page 2: Financial Terms
        story.append(Paragraph("ARTICLE IV: RENT AND FINANCIAL OBLIGATIONS", self.styles['SectionHeader']))
        
        story.append(Paragraph(
            f"<b>4.1 ANNUAL BASE RENT:</b> Tenant shall pay to Landlord annual base rent in the amount of "
            f"<b>${lease_data['annual_base_rent']:,}</b> (the \"<b>Annual Base Rent</b>\").",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>4.2 MONTHLY BASE RENT:</b> The Annual Base Rent shall be payable in equal monthly installments "
            f"of <b>${lease_data['monthly_base_rent']:,.2f}</b>, due and payable on the first day of each calendar "
            f"month during the Lease Term, without demand, deduction, or offset.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>4.3 BASE RENT PER SQUARE FOOT:</b> The base rent is calculated at a rate of "
            f"<b>${lease_data['base_rent_psf']:.2f} per rentable square foot</b> per annum.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>4.4 ANNUAL ESCALATION:</b> Commencing on the first anniversary of the Commencement Date, "
            f"and on each anniversary thereafter, the Annual Base Rent shall increase by "
            f"<b>{lease_data['annual_escalation_pct']}%</b> annually. Such increases shall be cumulative and compounding.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>4.5 ADDITIONAL RENT:</b> In addition to the Base Rent, Tenant shall pay as additional rent "
            f"Tenant's Pro Rata Share of Operating Expenses, estimated to be approximately "
            f"<b>${lease_data['additional_rent_estimate']:,.2f}</b> annually. Additional rent shall include, "
            f"without limitation, real property taxes, insurance premiums, common area maintenance (CAM), "
            f"utilities, and other operating expenses as defined in Article VIII.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>4.6 PRO RATA SHARE:</b> Tenant's proportionate share of building expenses shall be "
            f"<b>{lease_data['pro_rata_share']:.4f}</b> ({lease_data['pro_rata_share']*100:.2f}%), "
            f"calculated as the ratio of the Premises' rentable square footage to the total rentable "
            f"square footage of the building.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>4.7 SECURITY DEPOSIT:</b> Upon execution of this Lease, Tenant shall deposit with Landlord "
            f"the sum of <b>${lease_data['security_deposit']:,}</b> as security for the faithful performance "
            f"of Tenant's obligations hereunder (the \"<b>Security Deposit</b>\"). The Security Deposit shall "
            f"be held by Landlord without interest and may be applied against any amounts due from Tenant or "
            f"to remedy any default by Tenant.",
            self.styles['LeaseBody']
        ))
        
        # Financial summary table
        story.append(Spacer(1, 0.2*inch))
        financial_summary = [
            ["<b>RENT SCHEDULE SUMMARY</b>", ""],
            ["Annual Base Rent:", f"${lease_data['annual_base_rent']:,}"],
            ["Monthly Base Rent:", f"${lease_data['monthly_base_rent']:,.2f}"],
            ["Rate per RSF:", f"${lease_data['base_rent_psf']:.2f}"],
            ["Annual Escalation:", f"{lease_data['annual_escalation_pct']}%"],
            ["Estimated Annual Operating Expenses:", f"${lease_data['additional_rent_estimate']:,.2f}"],
            ["Security Deposit:", f"${lease_data['security_deposit']:,}"],
        ]
        
        t = Table(financial_summary, colWidths=[3.5*inch, 2.5*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        
        story.append(PageBreak())
        
        # Page 3: Use and Maintenance
        story.append(Paragraph("ARTICLE V: USE OF PREMISES", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"<b>5.1 PERMITTED USE:</b> The Premises shall be used and occupied solely for general office purposes "
            f"consistent with Tenant's {lease_data['industry_sector']} business operations, and for no other purpose "
            f"without the prior written consent of Landlord.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>5.2 COMPLIANCE WITH LAWS:</b> Tenant shall, at its sole cost and expense, promptly comply with "
            "all laws, ordinances, orders, rules, regulations, and requirements of all federal, state, and municipal "
            "governments and appropriate departments, commissions, boards, and officers thereof, which may be applicable "
            "to the Premises or to Tenant's use or occupation thereof.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE VI: MAINTENANCE AND REPAIRS", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>6.1 TENANT'S OBLIGATIONS:</b> Tenant shall, at its own cost and expense, keep and maintain the "
            "interior of the Premises, including all interior walls, floors, ceilings, fixtures, and equipment in "
            "good order, condition, and repair. Tenant shall be responsible for all repairs necessitated by the "
            "negligence or misuse of Tenant, its employees, agents, customers, or invitees.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>6.2 LANDLORD'S OBLIGATIONS:</b> Landlord shall maintain in good repair the structural portions "
            "of the building, including the roof, foundation, exterior walls, and common areas. Landlord shall "
            "maintain all building systems including HVAC, electrical, plumbing, and life safety systems, subject "
            "to reimbursement from Tenant as provided in the Additional Rent provisions.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE VII: INSURANCE AND INDEMNIFICATION", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>7.1 TENANT'S INSURANCE:</b> Tenant shall maintain throughout the Lease Term, at its sole cost "
            "and expense: (a) Commercial General Liability insurance with limits of not less than $2,000,000 per "
            "occurrence and $4,000,000 in the aggregate; (b) Property insurance covering all of Tenant's personal "
            "property, trade fixtures, and improvements; and (c) Workers' Compensation insurance as required by law.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>7.2 INDEMNIFICATION:</b> Tenant shall indemnify, defend, and hold harmless Landlord from and "
            "against any and all claims, actions, damages, liability, and expenses arising from Tenant's use of "
            "the Premises or from any activity, work, or thing done, permitted, or suffered by Tenant in or about "
            "the Premises, except to the extent caused by Landlord's negligence or willful misconduct.",
            self.styles['LeaseBody']
        ))
        
        story.append(PageBreak())
        
        # Page 4: Operating Expenses
        story.append(Paragraph("ARTICLE VIII: OPERATING EXPENSES AND ADDITIONAL RENT", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>8.1 OPERATING EXPENSES DEFINED:</b> \"Operating Expenses\" shall mean all costs and expenses "
            "incurred by Landlord in operating, maintaining, repairing, and managing the Building and the land "
            "upon which it is situated, including but not limited to:",
            self.styles['LeaseBody']
        ))
        
        operating_expenses = """
        (a) Real property taxes and assessments;<br/>
        (b) Insurance premiums for property, liability, and other insurance;<br/>
        (c) Utilities for common areas;<br/>
        (d) Landscaping and grounds maintenance;<br/>
        (e) Snow removal and exterior maintenance;<br/>
        (f) Common area cleaning and janitorial services;<br/>
        (g) Security services;<br/>
        (h) Property management fees (not to exceed 3% of gross rents);<br/>
        (i) Repairs and maintenance of building systems and equipment;<br/>
        (j) Capital improvements that reduce operating expenses or are required by law (amortized over useful life).
        """
        story.append(Paragraph(operating_expenses, self.styles['LeaseBody']))
        
        story.append(Paragraph(
            f"<b>8.2 TENANT'S SHARE:</b> Tenant shall pay, as Additional Rent, Tenant's Pro Rata Share "
            f"({lease_data['pro_rata_share']*100:.2f}%) of all Operating Expenses. Landlord shall provide "
            f"Tenant with an annual estimate of Operating Expenses, and Tenant shall pay one-twelfth of such "
            f"estimate on the first day of each month along with Base Rent.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>8.3 RECONCILIATION:</b> Within ninety (90) days after the end of each calendar year, Landlord "
            "shall provide Tenant with a statement of actual Operating Expenses. If Tenant's payments were less "
            "than Tenant's actual Pro Rata Share, Tenant shall pay the deficiency within thirty (30) days. If "
            "Tenant's payments exceeded its actual Pro Rata Share, Landlord shall credit such excess against "
            "future rent payments.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE IX: UTILITIES AND SERVICES", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>9.1 UTILITIES:</b> Landlord shall provide water, electricity, heat, ventilation, air conditioning, "
            "and other utilities to the Premises as reasonably required for normal office use during business hours "
            "(8:00 AM to 6:00 PM Monday through Friday, and 9:00 AM to 1:00 PM on Saturday, excluding holidays). "
            "After-hours HVAC service shall be available at Tenant's expense at the rate of $75 per hour per zone.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>9.2 JANITORIAL SERVICES:</b> Landlord shall provide janitorial services to the Premises five (5) "
            "nights per week, in accordance with the building's cleaning specifications. Additional cleaning services "
            "may be arranged by Tenant at Tenant's expense.",
            self.styles['LeaseBody']
        ))
        
        story.append(PageBreak())
        
        # Page 5: Alterations and Improvements
        story.append(Paragraph("ARTICLE X: ALTERATIONS AND IMPROVEMENTS", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>10.1 TENANT IMPROVEMENTS:</b> Tenant shall not make any alterations, additions, or improvements "
            "to the Premises without the prior written consent of Landlord, which consent shall not be unreasonably "
            "withheld for non-structural alterations costing less than $25,000.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>10.2 OWNERSHIP:</b> All alterations, additions, and improvements made to the Premises shall become "
            "the property of Landlord upon installation, except for Tenant's movable trade fixtures and equipment. "
            "Upon expiration or termination of this Lease, Tenant shall, at Landlord's option, remove any alterations "
            "and restore the Premises to its original condition, or leave such alterations in place.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XI: ASSIGNMENT AND SUBLETTING", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>11.1 RESTRICTION:</b> Tenant shall not assign this Lease or sublet all or any portion of the "
            "Premises without the prior written consent of Landlord, which consent shall not be unreasonably "
            "withheld, conditioned, or delayed. Any attempted assignment or subletting without such consent shall "
            "be void and shall constitute a material default under this Lease.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>11.2 PERMITTED TRANSFERS:</b> Notwithstanding the foregoing, Tenant may assign this Lease or "
            "sublet the Premises without Landlord's consent to (a) any entity that controls, is controlled by, or "
            "is under common control with Tenant, or (b) any entity that acquires all or substantially all of "
            "Tenant's assets or stock, provided that the assignee assumes all of Tenant's obligations hereunder "
            "and has a net worth equal to or greater than Tenant.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XII: DEFAULT AND REMEDIES", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>12.1 EVENTS OF DEFAULT:</b> The occurrence of any of the following shall constitute an Event of Default:",
            self.styles['LeaseBody']
        ))
        
        defaults = """
        (a) Failure to pay rent or other charges within five (5) days after written notice;<br/>
        (b) Failure to perform any other covenant or obligation within thirty (30) days after written notice;<br/>
        (c) Bankruptcy, insolvency, or assignment for the benefit of creditors;<br/>
        (d) Vacation or abandonment of the Premises;<br/>
        (e) Any other material breach of this Lease.
        """
        story.append(Paragraph(defaults, self.styles['LeaseBody']))
        
        story.append(Paragraph(
            "<b>12.2 LANDLORD'S REMEDIES:</b> Upon the occurrence of an Event of Default, Landlord may, in addition "
            "to any other remedies available at law or in equity: (a) terminate this Lease and Tenant's right to "
            "possession; (b) pursue an action for unpaid rent and damages; (c) re-enter and re-let the Premises on "
            "behalf of Tenant; or (d) pursue any other remedy available under applicable law.",
            self.styles['LeaseBody']
        ))
        
        story.append(PageBreak())
        
        # Page 6: Renewal and Termination Options
        story.append(Paragraph("ARTICLE XIII: RENEWAL OPTIONS", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"<b>13.1 RENEWAL RIGHTS:</b> Subject to the terms and conditions set forth herein, Tenant shall have "
            f"<b>{lease_data['renewal_options']}</b> to extend the Lease Term (each, a \"<b>Renewal Term</b>\"). "
            f"Each Renewal Term shall be upon the same terms and conditions as the initial Lease Term, except that "
            f"the Base Rent during each Renewal Term shall be at the then-prevailing market rate for comparable "
            f"space in the building and surrounding area.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            f"<b>13.2 EXERCISE OF OPTION:</b> To exercise a renewal option, Tenant must provide written notice "
            f"to Landlord not less than <b>{lease_data['renewal_notice_days']} days</b> prior to the expiration "
            f"of the then-current term. Time is of the essence with respect to the delivery of such notice. Failure "
            f"to timely deliver such notice shall result in the automatic waiver of the renewal option.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>13.3 CONDITIONS TO RENEWAL:</b> Tenant's right to exercise any renewal option is subject to the "
            "following conditions: (a) Tenant is not in default under this Lease at the time of exercise or at the "
            "commencement of the Renewal Term; (b) Tenant is occupying at least 75% of the Premises; and (c) this "
            "Lease has not been assigned (except for permitted transfers) or the Premises have not been sublet for "
            "more than 50% of the rentable area.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XIV: TERMINATION RIGHTS", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"<b>14.1 EARLY TERMINATION:</b> {lease_data['termination_rights']}",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>14.2 CASUALTY TERMINATION:</b> If the Premises or the Building are damaged by fire or other casualty "
            "to such extent that (a) the cost of restoration exceeds fifty percent (50%) of the replacement value, or "
            "(b) restoration cannot be completed within one hundred eighty (180) days, then either party may terminate "
            "this Lease upon thirty (30) days' written notice to the other party.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>14.3 CONDEMNATION:</b> If all or substantially all of the Premises are taken by eminent domain, "
            "this Lease shall automatically terminate as of the date of taking. If only a portion of the Premises "
            "is taken and the remainder is not suitable for Tenant's continued occupancy, Tenant may terminate this "
            "Lease upon sixty (60) days' written notice.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XV: GUARANTY", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"<b>15.1 GUARANTY REQUIREMENT:</b> {lease_data['guarantor']}",
            self.styles['LeaseBody']
        ))
        
        story.append(PageBreak())
        
        # Page 7: Additional Covenants
        story.append(Paragraph("ARTICLE XVI: PARKING", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"<b>16.1 PARKING SPACES:</b> Landlord shall provide Tenant with {max(3, lease_data['rentable_square_feet']//500)} "
            f"unreserved parking spaces in the building's parking facility at no additional charge. Additional parking "
            f"spaces may be leased by Tenant at the prevailing rate, subject to availability.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XVII: SIGNAGE", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>17.1 BUILDING STANDARD SIGNAGE:</b> Tenant shall be entitled to building-standard suite signage "
            "at the entrance to the Premises and a listing in the building directory. All signage shall be subject "
            "to Landlord's prior written approval and must comply with all applicable building standards and governmental "
            "requirements.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XVIII: ACCESS AND SECURITY", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>18.1 ACCESS:</b> Tenant and its employees shall have access to the Premises twenty-four (24) hours "
            "per day, seven (7) days per week, subject to the building's security procedures. After normal business "
            "hours, access may require use of an electronic access card or security clearance.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>18.2 LANDLORD ACCESS:</b> Landlord and its agents shall have the right to enter the Premises at "
            "reasonable times upon reasonable notice (except in emergencies) for the purpose of inspecting the "
            "Premises, making repairs, showing the Premises to prospective purchasers or tenants, or for any other "
            "purpose reasonably related to Landlord's rights or obligations under this Lease.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XIX: ENVIRONMENTAL COMPLIANCE", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>19.1 HAZARDOUS MATERIALS:</b> Tenant shall not cause or permit any Hazardous Materials (as defined "
            "by applicable environmental laws) to be brought upon, kept, used, stored, generated, or disposed of in, "
            "on, or about the Premises without the prior written consent of Landlord, except for ordinary office "
            "supplies in customary quantities used in compliance with all applicable laws.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph(
            "<b>19.2 INDEMNIFICATION:</b> Tenant shall indemnify, defend, and hold harmless Landlord from and against "
            "any and all claims, costs, and liabilities arising from Tenant's breach of its obligations under this "
            "Article XIX.",
            self.styles['LeaseBody']
        ))
        
        story.append(PageBreak())
        
        # Page 8: Miscellaneous Provisions
        story.append(Paragraph("ARTICLE XX: SUBORDINATION AND ATTORNMENT", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>20.1 SUBORDINATION:</b> This Lease shall be subject and subordinate to all ground leases, mortgages, "
            "and deeds of trust which now or hereafter affect the Building, and to all renewals, modifications, "
            "replacements, and extensions thereof, provided that the holder of any such encumbrance agrees to recognize "
            "Tenant's rights under this Lease and not disturb Tenant's possession so long as Tenant is not in default.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XXI: ESTOPPEL CERTIFICATES", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>21.1 TENANT'S CERTIFICATE:</b> Tenant shall, within ten (10) business days after request by Landlord, "
            "execute and deliver to Landlord an estoppel certificate certifying that this Lease is in full force and "
            "effect, the amount of rent being paid, the dates through which rent has been paid, and whether Tenant "
            "has any defenses or offsets against the enforcement of this Lease.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XXII: HOLDING OVER", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>22.1 HOLDOVER RENT:</b> If Tenant holds over after the expiration or earlier termination of this "
            "Lease without Landlord's written consent, Tenant shall pay rent equal to 150% of the rent in effect "
            "immediately prior to such expiration or termination. Such holdover tenancy shall be on a month-to-month "
            "basis and may be terminated by either party upon thirty (30) days' written notice.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XXIII: FORCE MAJEURE", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>23.1 EXCUSED PERFORMANCE:</b> Except for the payment of rent and other monetary obligations, neither "
            "party shall be liable for any delay or failure in performance caused by events beyond its reasonable control, "
            "including but not limited to acts of God, war, terrorism, strikes, labor disputes, governmental restrictions, "
            "or utilities failures (\"<b>Force Majeure Events</b>\").",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XXIV: BROKERS", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>24.1 BROKER REPRESENTATION:</b> Each party represents and warrants to the other that it has not dealt "
            "with any broker or finder in connection with this Lease except as may be expressly set forth in a separate "
            "brokerage agreement. Each party shall indemnify and hold the other harmless from any claims for brokerage "
            "commissions or finder's fees arising from any breach of this representation.",
            self.styles['LeaseBody']
        ))
        
        story.append(PageBreak())
        
        # Page 9: Final Provisions
        story.append(Paragraph("ARTICLE XXV: NOTICES", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>25.1 METHOD OF NOTICE:</b> All notices, demands, requests, or other communications required or "
            "permitted under this Lease shall be in writing and shall be deemed given when (a) delivered personally, "
            "(b) sent by recognized overnight courier service, or (c) sent by certified or registered mail, return "
            "receipt requested, postage prepaid, addressed as follows:",
            self.styles['LeaseBody']
        ))
        
        notice_addresses = f"""
        <b>To Landlord:</b><br/>
        {lease_data['landlord_name']}<br/>
        {lease_data['landlord_address']}<br/>
        Attention: Property Manager<br/>
        <br/>
        <b>To Tenant:</b><br/>
        {lease_data['tenant_name']}<br/>
        {lease_data['tenant_address']}<br/>
        Attention: Facilities Manager
        """
        story.append(Paragraph(notice_addresses, self.styles['LeaseBody']))
        
        story.append(Paragraph("ARTICLE XXVI: GOVERNING LAW", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"<b>26.1 APPLICABLE LAW:</b> This Lease shall be governed by and construed in accordance with the "
            f"laws of the State of {lease_data['property_state']}, without regard to its conflict of laws principles.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XXVII: ENTIRE AGREEMENT", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>27.1 INTEGRATION:</b> This Lease constitutes the entire agreement between the parties with respect "
            "to the subject matter hereof and supersedes all prior agreements, understandings, negotiations, and "
            "discussions, whether oral or written. This Lease may not be amended except by a written instrument "
            "signed by both parties.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XXVIII: SEVERABILITY", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>28.1 SEVERABILITY:</b> If any provision of this Lease is held to be invalid, illegal, or unenforceable, "
            "the validity, legality, and enforceability of the remaining provisions shall not be affected or impaired "
            "thereby.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XXIX: WAIVER", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>29.1 NO WAIVER:</b> No waiver by either party of any breach or default hereunder shall be deemed a "
            "waiver of any subsequent breach or default of the same or similar nature. No delay or omission in exercising "
            "any right or remedy shall impair such right or remedy or be construed as a waiver.",
            self.styles['LeaseBody']
        ))
        
        story.append(Paragraph("ARTICLE XXX: ATTORNEY'S FEES", self.styles['SectionHeader']))
        story.append(Paragraph(
            "<b>30.1 PREVAILING PARTY:</b> In the event of any litigation or other proceeding arising out of this "
            "Lease, the prevailing party shall be entitled to recover its reasonable attorney's fees and costs from "
            "the non-prevailing party.",
            self.styles['LeaseBody']
        ))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Page 10: Signature Page
        story.append(PageBreak())
        story.append(Paragraph("EXECUTION PAGE", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            "IN WITNESS WHEREOF, the parties hereto have executed this Lease as of the date first written above.",
            self.styles['LeaseBody']
        ))
        
        story.append(Spacer(1, 0.4*inch))
        
        # Landlord signature block
        story.append(Paragraph(f"<b>LANDLORD:</b>", self.styles['LeaseBody']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>{lease_data['landlord_name']}</b>", self.styles['LeaseBody']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("By: _________________________________", self.styles['LeaseBody']))
        story.append(Paragraph("Name: ______________________________", self.styles['LeaseBody']))
        story.append(Paragraph("Title: _______________________________", self.styles['LeaseBody']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", self.styles['LeaseBody']))
        
        story.append(Spacer(1, 0.6*inch))
        
        # Tenant signature block
        story.append(Paragraph(f"<b>TENANT:</b>", self.styles['LeaseBody']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>{lease_data['tenant_name']}</b>", self.styles['LeaseBody']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("By: _________________________________", self.styles['LeaseBody']))
        story.append(Paragraph("Name: ______________________________", self.styles['LeaseBody']))
        story.append(Paragraph("Title: _______________________________", self.styles['LeaseBody']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", self.styles['LeaseBody']))
        
        story.append(Spacer(1, 0.6*inch))
        
        # Footer
        story.append(Paragraph(
            "<i>This document constitutes a legally binding agreement. Both parties should retain a fully executed "
            "copy for their records. Exhibits and attachments, if any, are incorporated herein by reference.</i>",
            self.styles['SmallPrint']
        ))
        
        # Build PDF
        doc.build(story)
        print(f"✓ Generated: {filepath}")
        return filepath
    
    def generate_multiple_leases(self, count=10):
        """Generate multiple lease agreements"""
        print(f"\n{'='*70}")
        print(f"COMMERCIAL LEASE GENERATOR")
        print(f"{'='*70}\n")
        print(f"Generating {count} synthetic lease agreements...")
        print(f"Output directory: {self.output_dir}\n")
        
        generated_files = []
        for i in range(count):
            lease_data = self.generate_lease_data()
            filename = f"Commercial_Lease_{i+1:03d}_{lease_data['tenant_name'].replace(' ', '_')}.pdf"
            filepath = self.create_lease_pdf(lease_data, filename)
            generated_files.append(filepath)
        
        print(f"\n{'='*70}")
        print(f"✓ Successfully generated {count} lease agreements")
        print(f"{'='*70}\n")
        
        return generated_files


if __name__ == "__main__":
    # Generate 10 leases by default
    generator = LeaseGenerator()
    generator.generate_multiple_leases(count=10)

