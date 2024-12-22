def create_table_real_estate():
    return """
    -- Create schema if it doesn't exist
    CREATE SCHEMA IF NOT EXISTS schema_marketplace;
    
    -- Create table if it doesn't exist
    CREATE TABLE IF NOT EXISTS schema_marketplace.real_estate (
        url TEXT NOT NULL,
        city TEXT NULL,
        price varchar(25) NULL
    );

    -- Truncate the table to ensure clean data
    TRUNCATE TABLE schema_marketplace.real_estate;
    """


def transformation_real_estate():
    return """
    INSERT INTO schema_marketplace.real_estate (url, city, price)
    SELECT url, city, price 
    FROM raw_schema_marketplace.real_estate;
    """


def economic():
    return """
    CREATE SCHEMA IF NOT EXISTS schema_marketplace;
    CREATE TABLE IF NOT EXISTS schema_marketplace.economic (
        longitude DECIMAL(10,6),
        latitude DECIMAL(10,6),
        city TEXT,
        working_age_population TEXT,
        employed_population TEXT,
        unemployed_population TEXT,
        employment_rate TEXT,
        avg_annual_income TEXT,
        median_annual_income TEXT,
        PRIMARY KEY (longitude, latitude)
    );

    TRUNCATE TABLE schema_marketplace.economic;

    WITH parsed_data AS (
        SELECT 
            NULLIF(SPLIT_PART(geo_location, ',', 2), '')::DECIMAL(10,6) as longitude,
            NULLIF(SPLIT_PART(geo_location, ',', 1), '')::DECIMAL(10,6) as latitude,
            city,
            CAST(working_age_population AS TEXT),
            CAST(employed_population AS TEXT),
            CAST(unemployed_population AS TEXT),
            CAST(employment_rate AS TEXT),
            CAST(avg_annual_income AS TEXT),
            CAST(median_annual_income AS TEXT)
        FROM raw_schema_marketplace.generate_economic_slocator_data
        WHERE geo_location IS NOT NULL
    )
    INSERT INTO schema_marketplace.economic
    SELECT 
        longitude,
        latitude,
        city,
        working_age_population,
        employed_population,
        unemployed_population,
        employment_rate,
        avg_annual_income,
        median_annual_income
    FROM parsed_data
    WHERE longitude IS NOT NULL
    AND latitude IS NOT NULL;
    """


def household():
    return """
CREATE SCHEMA IF NOT EXISTS schema_marketplace;
CREATE TABLE IF NOT EXISTS schema_marketplace.household (
    longitude DECIMAL(10,6),
    latitude DECIMAL(10,6),
    country TEXT,
    city TEXT,
    household_average_size TEXT,
    household_median_size TEXT,
    PRIMARY KEY (longitude, latitude)
);

TRUNCATE TABLE schema_marketplace.household;

WITH combined_data AS (
    -- Saudi Arabia Household Data
    SELECT
        NULLIF(SPLIT_PART(SPLIT_PART("Degree", ' ', 1), ' ', 1), '')::DECIMAL(10,6) as longitude,
        NULLIF(SPLIT_PART(SPLIT_PART("Degree", ' ', 2), ' ', 1), '')::DECIMAL(10,6) as latitude,
        'Saudi Arabia' as country,
        "Location" as city,
        COALESCE(CAST("Household Average Size" AS TEXT), '') as household_average_size,
        COALESCE(CAST("Household Median Size" AS TEXT), '') as household_median_size
    FROM raw_schema_marketplace.household

    UNION ALL

    -- Canada Household Data
    SELECT
        NULLIF(SPLIT_PART(geo_location, ',', 2), '')::DECIMAL(10,6) as longitude,
        NULLIF(SPLIT_PART(geo_location, ',', 1), '')::DECIMAL(10,6) as latitude,
        'Canada' as country,
        CASE 
            WHEN NULLIF(SPLIT_PART(geo_location, ',', 1), '')::DECIMAL(10,6) BETWEEN 43.4 AND 43.9 
                AND NULLIF(SPLIT_PART(geo_location, ',', 2), '')::DECIMAL(10,6) BETWEEN -79.5 AND -79.2 THEN 'Toronto'
            WHEN NULLIF(SPLIT_PART(geo_location, ',', 1), '')::DECIMAL(10,6) BETWEEN 45.4 AND 45.7 
                AND NULLIF(SPLIT_PART(geo_location, ',', 2), '')::DECIMAL(10,6) BETWEEN -73.7 AND -73.4 THEN 'Montreal'
            ELSE 'Other'
        END as city,
        COALESCE(CAST("Household Average Size" AS TEXT), '') as household_average_size,
        COALESCE(CAST("Household Median Size" AS TEXT), '') as household_median_size
    FROM raw_schema_marketplace.generate_household_slocator_data
),
ranked_data AS (
    SELECT
        longitude,
        latitude,
        country,
        city,
        household_average_size,
        household_median_size,
        ROW_NUMBER() OVER (
            PARTITION BY longitude, latitude
            ORDER BY household_average_size DESC NULLS LAST
        ) as rn
    FROM combined_data
    WHERE longitude IS NOT NULL
    AND latitude IS NOT NULL
)
INSERT INTO schema_marketplace.household (
    longitude,
    latitude,
    country,
    city,
    household_average_size,
    household_median_size
)
SELECT
    longitude,
    latitude,
    country,
    city,
    household_average_size,
    household_median_size
FROM ranked_data
WHERE rn = 1;
    """


def housing():
    return """
CREATE SCHEMA IF NOT EXISTS schema_marketplace;
CREATE TABLE IF NOT EXISTS schema_marketplace.housing (
    longitude DECIMAL(10,6),
    latitude DECIMAL(10,6),
    country TEXT,
    city TEXT,
    total_dwellings TEXT,
    residential_dwellings TEXT,
    owned_dwellings TEXT,
    rented_dwellings TEXT,
    provided_dwellings TEXT,
    other_residential_dwellings TEXT,
    non_residential_dwellings TEXT,
    public_housing TEXT,
    work_camps TEXT,
    commercial_dwellings TEXT,
    other_dwellings TEXT,
    PRIMARY KEY (longitude, latitude)
);

TRUNCATE TABLE schema_marketplace.housing;

WITH combined_data AS (
    -- Saudi Arabia Housing Data
    SELECT
        NULLIF(SPLIT_PART(SPLIT_PART("Degree", ' ', 1), ' ', 1), '')::DECIMAL(10,6) as longitude,
        NULLIF(SPLIT_PART(SPLIT_PART("Degree", ' ', 2), ' ', 1), '')::DECIMAL(10,6) as latitude,
        'Saudi Arabia' as country,
        "Location" as city,
        CAST("Total Dwellings" AS TEXT) as total_dwellings,
        CAST("Residential Dwellings" AS TEXT) as residential_dwellings,
        CAST("Owned Dwellings" AS TEXT) as owned_dwellings,
        CAST("Rented Dwellings" AS TEXT) as rented_dwellings,
        CAST("Provided Dwellings" AS TEXT) as provided_dwellings,
        CAST("Other Residential Dwellings" AS TEXT) as other_residential_dwellings,
        COALESCE(CAST("Non-Residential Dwellings" AS TEXT), '') as non_residential_dwellings,
        COALESCE(CAST("Public Housing" AS TEXT), '') as public_housing,
        COALESCE(CAST("Work Camps" AS TEXT), '') as work_camps,
        COALESCE(CAST("Commercial Dwellings" AS TEXT), '') as commercial_dwellings,
        COALESCE(CAST("Other Dwellings" AS TEXT), '') as other_dwellings
    FROM raw_schema_marketplace.housing

    UNION ALL

    -- Canada Housing Data
    SELECT
        NULLIF(SPLIT_PART(geo_location, ',', 2), '')::DECIMAL(10,6) as longitude,
        NULLIF(SPLIT_PART(geo_location, ',', 1), '')::DECIMAL(10,6) as latitude,
        'Canada' as country,
        CASE 
            WHEN NULLIF(SPLIT_PART(geo_location, ',', 1), '')::DECIMAL(10,6) BETWEEN 43.4 AND 43.9 
                AND NULLIF(SPLIT_PART(geo_location, ',', 2), '')::DECIMAL(10,6) BETWEEN -79.5 AND -79.2 THEN 'Toronto'
            WHEN NULLIF(SPLIT_PART(geo_location, ',', 1), '')::DECIMAL(10,6) BETWEEN 45.4 AND 45.7 
                AND NULLIF(SPLIT_PART(geo_location, ',', 2), '')::DECIMAL(10,6) BETWEEN -73.7 AND -73.4 THEN 'Montreal'
            ELSE 'Other'
        END as city,
        COALESCE(CAST("Total Dwellings" AS TEXT), '') as total_dwellings,
        COALESCE(CAST("Residential Dwellings" AS TEXT), '') as residential_dwellings,
        COALESCE(CAST("Owned Dwellings" AS TEXT), '') as owned_dwellings,
        COALESCE(CAST("Rented Dwellings" AS TEXT), '') as rented_dwellings,
        COALESCE(CAST("Provided Dwellings" AS TEXT), '') as provided_dwellings,
        COALESCE(CAST("Other Residential Dwellings" AS TEXT), '') as other_residential_dwellings,
        COALESCE(CAST("Non-Residential Dwellings" AS TEXT), '') as non_residential_dwellings,
        COALESCE(CAST("Public Housing" AS TEXT), '') as public_housing,
        COALESCE(CAST("Work Camps" AS TEXT), '') as work_camps,
        COALESCE(CAST("Commercial Dwellings" AS TEXT), '') as commercial_dwellings,
        COALESCE(CAST("Other Dwellings" AS TEXT), '') as other_dwellings
    FROM raw_schema_marketplace.generate_housing_slocator_data
),
ranked_data AS (
    SELECT
        longitude,
        latitude,
        country,
        city,
        total_dwellings,
        residential_dwellings,
        owned_dwellings,
        rented_dwellings,
        provided_dwellings,
        other_residential_dwellings,
        non_residential_dwellings,
        public_housing,
        work_camps,
        commercial_dwellings,
        other_dwellings,
        ROW_NUMBER() OVER (
            PARTITION BY longitude, latitude
            ORDER BY total_dwellings DESC NULLS LAST
        ) as rn
    FROM combined_data
    WHERE longitude IS NOT NULL
    AND latitude IS NOT NULL
)
INSERT INTO schema_marketplace.housing
SELECT
    longitude,
    latitude,
    country,
    city,
    total_dwellings,
    residential_dwellings,
    owned_dwellings,
    rented_dwellings,
    provided_dwellings,
    other_residential_dwellings,
    non_residential_dwellings,
    public_housing,
    work_camps,
    commercial_dwellings,
    other_dwellings
FROM ranked_data
WHERE rn = 1;
   """


def population():
    return """
CREATE SCHEMA IF NOT EXISTS schema_marketplace;
CREATE TABLE IF NOT EXISTS schema_marketplace.population (
    longitude DECIMAL(10,6),
    latitude DECIMAL(10,6),
    country TEXT,
    city TEXT,
    population TEXT,
    population_density TEXT,
    male_population TEXT,
    female_population TEXT,
    median_age_male TEXT,
    median_age_female TEXT,
    PRIMARY KEY (longitude, latitude)
);

TRUNCATE TABLE schema_marketplace.population;

WITH combined_data AS (
    -- Saudi Arabia Census Data
    SELECT
        NULLIF(SPLIT_PART(SPLIT_PART("Degree", ' ', 1), ' ', 1), '')::DECIMAL(10,6) as longitude,
        NULLIF(SPLIT_PART(SPLIT_PART("Degree", ' ', 2), ' ', 1), '')::DECIMAL(10,6) as latitude,
        'Saudi Arabia' as country,
        "Location" as city,
        "Total Population" as population,
        "Population Density" as population_density,
        "Male Population" as male_population,
        "Female Population" as female_population,
        "Median Age (Male)" as median_age_male,
        "Median Age (Female)" as median_age_female
    FROM raw_schema_marketplace.population
    where "Zoom Level" = 6

    UNION ALL

    -- Canada Census Data
    SELECT
        NULLIF(longitude, NULL)::DECIMAL(10,6),
        NULLIF(latitude, NULL)::DECIMAL(10,6),
        'Canada' as country,
        CASE 
            WHEN latitude BETWEEN 43.4 AND 43.9 
                AND longitude BETWEEN -79.5 AND -79.2 THEN 'Toronto'
            WHEN latitude BETWEEN 45.4 AND 45.7 
                AND longitude BETWEEN -73.7 AND -73.4 THEN 'Montreal'
            ELSE 'Other'
        END as city,
        CAST(population_2021 AS TEXT) as population,
        CAST(population_density_per_square_kilometre_2021 AS TEXT) as population_density,
        NULL as male_population,
        NULL as female_population,
        NULL as median_age_male,
        NULL as median_age_female
    FROM raw_schema_marketplace.canada_census
),
ranked_data AS (
    SELECT
        longitude,
        latitude,
        country,
        city,
        population,
        population_density,
        male_population,
        female_population,
        median_age_male,
        median_age_female,
        ROW_NUMBER() OVER (
            PARTITION BY longitude, latitude
            ORDER BY population DESC NULLS LAST
        ) as rn
    FROM combined_data
    WHERE longitude IS NOT NULL
    AND latitude IS NOT NULL
)
INSERT INTO schema_marketplace.population (
    longitude,
    latitude,
    country,
    city,
    population,
    population_density,
    male_population,
    female_population,
    median_age_male,
    median_age_female
)
SELECT
    longitude,
    latitude,
    country,
    city,
    population,
    population_density,
    male_population,
    female_population,
    median_age_male,
    median_age_female
FROM ranked_data
WHERE rn = 1;
    """