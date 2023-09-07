import streamlit as st
import pandas as pd
import numpy as np
import io
import xlsxwriter


uploaded_file = st.file_uploader("Please Upload CSV File", type=['csv'])

if uploaded_file is not None:
    #read csv
    dfpreclean=pd.read_csv(uploaded_file)
else:
    st.warning("you need to upload a csv file.")

buffer = io.BytesIO()

dfpreclean.drop(['id','merchant_id','user_id','customer_id','subtotal','tax','is_manual','success','donation','tip','meta','pre_auth','updated_at','source'], axis=1, inplace=True)
dfpreclean2 = dfpreclean[(dfpreclean['type'].isna() == False) & (dfpreclean['total'].isna() == False)]
dfpreclean3 = dfpreclean2[(dfpreclean2['payment_method'] == 'card') | (dfpreclean2['payment_method'] == 'bank')]
dfpreclean4 = dfpreclean3[dfpreclean3['type'] == 'charge']
dfpreclean4["channel"].fillna("blank", inplace = True)
dfpreclean4["memo"].fillna("blank", inplace = True)
dfpreclean4["payment_note"].fillna("blank", inplace = True)
df = dfpreclean4


totalsum = np.sum(df['total'])

total_transactions = df['type'].count()
mean_transaction = np.mean(df['total'])
median_transaction = np.median(df['total'])
max_transaction = np.max(df['total'])
total_unique_customer_last_four = df['payment_last_four'].nunique()
total_unique_customer_names = df['payment_person_name'].nunique()

dfgroupname = df.groupby(['payment_person_name']).agg(
         tran_count=('total', 'count'),
         tran_sum=('total', np.sum)
)

dfgrouplastfour = df.groupby(['payment_last_four']).agg(
         tran_count=('total', 'count'),
         tran_sum=('total', np.sum)
)

avg_transactions_count_per_customer_name = np.mean(dfgroupname['tran_count'])
avg_transactions_sum_per_customer_name = np.mean(dfgroupname['tran_sum'])
avg_transactions_count_per_customer_last_four = np.mean(dfgrouplastfour['tran_count'])
avg_transactions_sum_per_customer_last_four = np.mean(dfgrouplastfour['tran_sum'])

dfcalc = pd.DataFrame({'totalsum':[totalsum],
                       'total_transactions':[total_transactions],
                       'mean_transaction':[mean_transaction],
                       'median_transaction':[median_transaction],
                       'max_transaction':[max_transaction],
                       'total_unique_customer_last_four':[total_unique_customer_last_four],
                       'total_unique_customer_names':[total_unique_customer_names],
                       'avg_transactions_count_per_customer_name':[avg_transactions_count_per_customer_name],
                       'avg_transactions_sum_per_customer_name':[avg_transactions_sum_per_customer_name],
                       'avg_transactions_count_per_customer_last_four':[avg_transactions_count_per_customer_last_four],
                       'avg_transactions_sum_per_customer_last_four':[avg_transactions_sum_per_customer_last_four]
                       })

format_mapping = {"totalsum": '${:,.2f}',
                  "total_transactions": '{:,.0f}', 
                  "mean_transaction": '${:,.2f}',
                  "median_transaction": '${:,.2f}',
                  "max_transaction": '${:,.2f}',
                  "total_unique_customer_last_four": '{:,.0f}',
                  "total_unique_customer_names": '{:,.0f}',
                  "avg_transactions_count_per_customer_name": '{:,.2f}',
                  "avg_transactions_sum_per_customer_name": '${:,.2f}',
                  "avg_transactions_count_per_customer_last_four": '{:,.2f}',
                  "avg_transactions_sum_per_customer_last_four": '${:,.2f}' 
                  }

for key, value in format_mapping.items():
        dfcalc[key] = dfcalc[key].apply(value.format)

#dfcalc2 = dfcalc.style.format(format_mapping)


pivottablenames = pd.pivot_table(df, index=['payment_person_name'], aggfunc={'payment_person_name': 'count', 'total': np.sum})
pivottablenames['totalpercent'] = (pivottablenames['total']/totalsum).apply('{:.2%}'.format)
pivottablenames['total'] = pivottablenames['total'].apply('${:,.2f}'.format)

pivottablelastfour = pd.pivot_table(df, index=['payment_last_four'], aggfunc={'payment_last_four': 'count', 'total': np.sum})
pivottablelastfour['totalpercent'] = (pivottablelastfour['total']/totalsum).apply('{:.2%}'.format)
pivottablelastfour['total'] = pivottablelastfour['total'].apply('${:,.2f}'.format)

pivottablechannel = pd.pivot_table(df, index=['channel'], aggfunc={'payment_last_four': 'count', 'total': np.sum})
pivottablechannel['totalpercent'] = (pivottablechannel['total']/totalsum).apply('{:.2%}'.format)
pivottablechannel['total'] = pivottablechannel['total'].apply('${:,.2f}'.format)

payment_note = df[df['payment_note'].isna() == False]
flagged_words = '2024|2025|2026|late|delinquent|month|months|quarter|year|CBD|medicine|drugs|\
                 loan|bail|bond|bankruptcy|bankrupt|18|21|vape|weed|career|advice|date|dating\
                 tinder|bumble|escort|sex|massage|vibrator|solar|solar panel|warranty|warranties\
                 Cuba|Iran|North Korea|Sudan|Syria|penny|credit|identity|currency|crypto|bitcoin|\
                 Ethereum|nft|Cryptocurrencies|Tether|bnb|xrp|dogecoin|cardano|solano|tron|polygon|\
                 debt|cruise|airplane|jet|charter|Tobacco|Cigarettes|egic|cigarette|theft|elimination|\
                 eliminate|reduce|reduction|colsult|consulting|wallet|prepaid|commodity|security|trading\
                 toy|airline|airplane|collection|enhance|occult|psychic|future|discount|Ammunition|gun|\
                 Silencers|Suppressors|ammo|supplement|Nutraceuticals|enhance|growth|stock|equity|donation|\
                 shipping|forwarding|adult|xxx|bride|occult|mail order|mailorder|restricted|video|penny|bidding|\
                 bid|travel|Telemarketing|videotext|membership|club|coupon|insurance|dental|dentist|Distressed|\
                 property|gamble|gambling|lottery|lotteries|gaming|fantasy|contest|sweepstake|incentive|prize|\
                 lending|interest|title|loan|investment|rich|alcohol|beer|wine|liquor|pharmacy|Pharmacies|marijuana|\
                 420|Infomercial|pawn|rebate|timeshare|time shares|resale|resell|sports|odds|forecasting|up sell|upsell|\
                 upsale|rich|quick|broker|deal|fast|dispensaries|dispensary|money|transfer|wire|transmitter|check|cashing|\
                 cash|mlm|Multi-Level Marketing|pre paid|prepaid|phone|flip|flipping|real estate|realestate|mobile|\
                 virtual|credit|re-sold|meta|Pharmaceuticals|Quasi|social|free|period|negative|reputation|subscription|\
                 trial|pay only for shipping'

payment_note_final = payment_note[payment_note['payment_note'].str.contains(flagged_words, case=False)]

memo = df[df['memo'].isna() == False]
badwords = 'bbb|yelp|fraud|scam|report|sloppy|shady|broken|imporsonation|\
            bad|not working|shady|horrible|negative|rotten|poor|terrible|\
            abysmal|awful|inaccurate|low quality|mediocre|nasty|abuse|worst|\
            worse|angry|pissed|disgusting|no show|alarming|atrocious|adverse|\
            alarming|angry|annoy|anxious|apathy|appalling|banal|barbed|belligerent|\
            bemoan|beneath|boring|broken|callous|cant|clumsy|coarse|cold|cold-hearted|\
            collapse|confused|contradictory|contrary|corrosive|corrupt|crazy|creepy|\
            criminal|cruel|cry|cutting|damaged|damage|damaging|dastardly|dead|decaying|\
            deformed|deny|deplorable|depressed|deprived|despicable|detrimental|dirty|\
            disease|disgusting|disheveled|dishonest|dishonorable|dismal|distress|dont|\
            dreadful|dreary|enraged|eroding|evil|fail|failing|faulty|fear|feeble|fight|\
            filthy|foul|frighten|frightful|gawky|ghastly|grave|greed|greedy|grim|grimace|\
            gross|grotesque|gruesome|guilty|haggard|hard|hard-hearted|harmful|hate|hideous|\
            homely|horrendous|horrible|hostile|hurt|hurtful|icky|ignorant|ignore|ill|immature|\
            imperfect|impossible|inane|inelegant|infernal|injure|injurious|insane|insidious|\
            insipid|jealous|junk|lose|lousy|lumpy|malicious|mean|menacing|messy|misshapenmissing|\
            misunderstood|moan|moldy|monstrous|naive|nasty|naughty|negate|negative|never|nonobody|\
            nondescript|nonsense|not|noxious|objectionable|odious|offensive|old|oppressive|pain|\
            perturb|pessimistic|petty|plain|poisonous|poor|prejudice|questionable|quirky|quit|\
            reject|renege|repellant|repell|reptilian|repugnant|repulsive|revenge|revolting|rocky\
            |rotten|rude|ruthless|sad|savage|scare|scary|scream|severe|shocking|shoddy|sick|sickening|\
            sinister|slimy|smelly|sobbing|sorry|spiteful|sticky|stinky|stormy|stressful|stuck|stupid|\
            substandard|suspect|suspicious|tense|terrible|terrifying|threatening|ugly|undermine|unfair|\
            unfavorable|unhappy|unhealthy|unjust|unlucky|unpleasant|unsatisfactory|unsightly|untoward|\
            unwanted|unwelcome|unwholesome|unwieldy|unwise|upset|vice|vicious|vile|villainous|vindictive|\
            wary|weary|wicked|woeful|worthless|wound|yell|yucky|zero'

memofinal = memo[memo['memo'].str.contains(badwords, case=False)]

dup = df
dup['payment_person_name_next'] = dup['payment_person_name'].shift(1)
dup['payment_person_name_prev'] = dup['payment_person_name'].shift(-1)
dup['payment_last_four_next'] = dup['payment_last_four'].shift(1)
dup['payment_last_four_prev'] = dup['payment_last_four'].shift(-1)
dup['created_at_day'] = dup['created_at'].str.split(expand=True)[0]
dup['created_at_dayprev'] = dup['created_at_day'].shift(-1)
dup['created_at_daynext'] = dup['created_at_day'].shift(1)
dup['created_at_time'] = dup['created_at'].str.split(expand=True)[1]
dup['totalmins'] = dup['created_at_time'].str.split(pat=":", expand=True)[0].astype(float) * 60 + dup['created_at_time'].str.split(pat=":", expand=True)[1].astype(float)
dup['totalminsprev'] = dup['totalmins'].shift(-1)
dup['totalminsnext'] = dup['totalmins'].shift(1)
dup2 = dup.query('created_at_day == created_at_daynext | created_at_day == created_at_dayprev')
dup3 = dup2.query('totalmins < totalminsprev + 60 | totalmins > totalminsnext - 60')
dup4 = dup3.query('payment_person_name == payment_person_name_next | \
         payment_person_name == payment_person_name_prev | \
         payment_last_four == payment_last_four_next | \
         payment_last_four == payment_last_four_prev')



# Create a Pandas Excel writer using XlsxWriter as the engine.
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    # Write each dataframe to a different worksheet.
    df.to_excel(writer, sheet_name='Clean_Data')
    dfcalc.to_excel(writer, sheet_name='Calculations')
    payment_note_final.to_excel(writer, sheet_name='Flagged_Payment_Notes')
    memofinal.to_excel(writer, sheet_name='Negative_Memo')
    pivottablenames.to_excel(writer, sheet_name='Names_Pivot')
    pivottablelastfour.to_excel(writer, sheet_name='Last_Four_Pivot')
    pivottablechannel.to_excel(writer, sheet_name='Chanel_Pivot')
    dup4.to_excel(writer, sheet_name='Dup_Trans')

    # Close the Pandas Excel writer and output the Excel file to the buffer
    writer.close()

    st.download_button(
        label="Download Excel worksheets",
        data=buffer,
        file_name="cleantransactions.xlsx",
        mime="application/vnd.ms-excel"
    )