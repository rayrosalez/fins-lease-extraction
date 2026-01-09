-- Landlords by News Sentiment Dataset
-- Distribution of landlord news sentiment

SELECT 
    COALESCE(recent_news_sentiment, 'Unknown') as sentiment,
    COUNT(*) as count
FROM ${catalog}.${schema}.landlords
GROUP BY recent_news_sentiment
ORDER BY 
    CASE 
        WHEN recent_news_sentiment = 'POSITIVE' THEN 1
        WHEN recent_news_sentiment = 'NEUTRAL' THEN 2
        WHEN recent_news_sentiment = 'NEGATIVE' THEN 3
        ELSE 4
    END
