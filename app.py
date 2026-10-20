import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import seaborn as sns
import matplotlib .pyplot as plt
import pymysql
import plotly.express as px
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="13849#Datasci",
    database="movie_analytics"
)
st.title("MOVIE ANALYTICS DASHBOARD")
st.set_page_config(
    page_title="CineScope Dashboard",
    page_icon="🎬",
    layout="wide"
)
movies = pd.read_sql("SELECT * FROM movies", conn)
cast = pd.read_sql("SELECT * FROM cast", conn)
crew = pd.read_sql("SELECT * FROM crew", conn)
genres = pd.read_sql("SELECT * FROM genres", conn)
movie_genres = pd.read_sql("SELECT * FROM movie_genres", conn)
movie_keywords = pd.read_sql("SELECT * FROM movie_keywords", conn)

with st.sidebar:
    selected = option_menu(
        "MENU",
        ["Filters", "Dashboard", "Query Explorer"],
        icons=["funnel", "bar-chart", "database"],
        menu_icon="camera-reels",
        default_index=0
    )
    
    
if selected == "Filters":
    
    st.header("🎬 Movie Filters")
    st.write("Filter movies by release year, language, and rating.")

    col1, col2, col3 = st.columns(3)

    with col1:
        years = sorted(
            movies["release_year"].dropna().unique().tolist()
        )

        year = st.selectbox(
            "Release Year",
            ["All"] + years
        )

    with col2:
        languages = sorted(
            movies["original_language"].dropna().unique().tolist()
        )

        language = st.selectbox(
            "Language",
            ["All"] + languages
        )

    with col3:
        rating = st.slider(
            "Minimum Rating",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.5
        )

    # Apply filters
    filtered_movies = movies.copy()

    if year != "All":
        filtered_movies = filtered_movies[
            filtered_movies["release_year"] == int(year)
        ]

    if language != "All":
        filtered_movies = filtered_movies[
            filtered_movies["original_language"] == language
        ]

    filtered_movies = filtered_movies[
        filtered_movies["vote_average"] >= rating
    ]

    # Display results
    st.divider()

    col1, col2 = st.columns(2)

    col1.metric("Movies Found", len(filtered_movies))

    avg_rating = (
        round(filtered_movies["vote_average"].mean(), 2)
        if not filtered_movies.empty
        else "N/A"
    )

    col2.metric("Average Rating", avg_rating)

    st.subheader("Filtered Movie Details")

    st.dataframe(
        filtered_movies,
        use_container_width=True,
        hide_index=True
    )
    
    
# ---------------- DASHBOARD ----------------
elif selected == "Dashboard":

    st.header("🎬 Movie Analytics Dashboard")
    st.write("Explore movie industry trends and performance.")

    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🎥 Total Movies",
        f"{movies['movie_id'].nunique():,}"
    )

    col2.metric(
        "⭐ Average Rating",
        f"{movies['vote_average'].mean():.2f} / 10"
    )

    col3.metric(
        "⏱️ Average Runtime",
        f"{movies['runtime'].mean():.0f} min"
    )

    col4.metric(
        "🌍 Languages",
        movies["original_language"].nunique()
    )

    st.divider()

    # Create two columns for charts
    col1, col2 = st.columns(2)

    # Chart 1: Rating Distribution
    with col1:
        st.subheader("⭐ Movie Rating Distribution")

        fig1 = px.histogram(
            movies,
            x="vote_average",
            nbins=20,
            title="Distribution of Movie Ratings",
            labels={
                "vote_average": "Average Rating",
                "count": "Number of Movies"
            },
            color_discrete_sequence=["#636EFA"]
        )

        fig1.update_layout(
            template="plotly_white",
            xaxis_title="Average Rating",
            yaxis_title="Number of Movies"
        )

        st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Movies Released Per Year
    with col2:
        st.subheader("📅 Movies Released Per Year")

        yearly_movies = (
            movies.groupby("release_year")["movie_id"]
            .nunique()
            .reset_index(name="movie_count")
            .sort_values("release_year")
        )

        fig2 = px.line(
            yearly_movies,
            x="release_year",
            y="movie_count",
            markers=True,
            title="Yearly Movie Releases",
            labels={
                "release_year": "Release Year",
                "movie_count": "Number of Movies"
            }
        )

        fig2.update_traces(
            line=dict(width=3),
            marker=dict(size=7)
        )

        fig2.update_layout(
            template="plotly_white",
            xaxis_title="Release Year",
            yaxis_title="Number of Movies"
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Chart 3: Budget vs Revenue
    st.subheader("💰 Movie Budget vs Revenue")

    valid_movies = movies[
        (movies["budget"] > 0) &
        (movies["revenue"] > 0)
    ]

    if not valid_movies.empty:

        fig3 = px.scatter(
            valid_movies,
            x="budget",
            y="revenue",
            hover_name="title",
            color="vote_average",
            size="vote_count",
            title="Movie Budget vs Revenue",
            labels={
                "budget": "Budget",
                "revenue": "Revenue",
                "vote_average": "Average Rating",
                "vote_count": "Number of Votes"
            },
            color_continuous_scale="Viridis"
        )

        fig3.update_layout(
            template="plotly_white",
            xaxis_title="Budget",
            yaxis_title="Revenue"
        )

        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("No movies with valid budget and revenue are available.")

    st.divider()

    # Chart 4: Average Rating by Language
    st.subheader("🌍 Average Rating by Language")

    language_ratings = (
        movies.groupby("original_language")
        .agg(
            average_rating=("vote_average", "mean"),
            movie_count=("movie_id", "nunique")
        )
        .reset_index()
        .sort_values("average_rating", ascending=False)
        .head(10)
    )

    fig4 = px.bar(
        language_ratings,
        x="original_language",
        y="average_rating",
        hover_data=["movie_count"],
        title="Top 10 Languages by Average Movie Rating",
        labels={
            "original_language": "Language Code",
            "average_rating": "Average Rating",
            "movie_count": "Number of Movies"
        },
        color="average_rating",
        color_continuous_scale="Blues"
    )

    fig4.update_layout(
        template="plotly_white",
        xaxis_title="Language",
        yaxis_title="Average Rating"
    )

    st.plotly_chart(fig4, use_container_width=True)

    # Footer
    st.divider()
    st.caption("CineScope | TMDB Movie Analytics Dashboard")



elif selected == "Query Explorer":

    st.title("🎬 SQL Query Explorer")

    option = st.selectbox(
        "Select a query",
        (
            "1. Top 10 Highest-Grossing Movies",
            "2. Top 10 Highest-Rated Movies",
            "3. Action Movies Released After 2015",
            "4. Average Budget and Revenue by Genre",
            "5. Top 10 Most Popular Movies",
            "6. Directors with More Than 3 Movies",
            "7. Top 10 Actors by Movie Count",
            "8. Movies with Profit Greater Than Average Profit",
            "9. Genres with Average Rating Above 7",
            "10. Movies Released Per Year"
        )
    )

    if option == "1. Top 10 Highest-Grossing Movies":
        df = pd.read_sql_query(
            """
            SELECT
                title,
                budget,
                revenue
            FROM movies
            WHERE revenue > 0
            ORDER BY revenue DESC
            LIMIT 10
            """,
            conn
        )

    elif option == "2. Top 10 Highest-Rated Movies":
        df = pd.read_sql_query(
            """
            SELECT
                title,
                vote_average,
                vote_count
            FROM movies
            WHERE vote_count > 0
            ORDER BY vote_average DESC, vote_count DESC
            LIMIT 10
            """,
            conn
        )

    elif option == "3. Action Movies Released After 2015":
        df = pd.read_sql_query(
            """
            SELECT DISTINCT
                m.title,
                m.release_date,
                m.vote_average
            FROM movies m
            JOIN movie_genres mg
                ON m.movie_id = mg.movie_id
            JOIN genres g
                ON mg.genre_id = g.genre_id
            WHERE g.genre_name = 'Action'
              AND m.release_date >= '2016-01-01'
            ORDER BY m.release_date
            """,
            conn
        )

    elif option == "4. Average Budget and Revenue by Genre":
        df = pd.read_sql_query(
            """
            SELECT
                g.genre_name,
                ROUND(AVG(m.budget), 2) AS average_budget,
                ROUND(AVG(m.revenue), 2) AS average_revenue,
                COUNT(DISTINCT m.movie_id) AS movie_count
            FROM movies m
            JOIN movie_genres mg
                ON m.movie_id = mg.movie_id
            JOIN genres g
                ON mg.genre_id = g.genre_id
            GROUP BY g.genre_id, g.genre_name
            ORDER BY average_revenue DESC
            """,
            conn
        )

    elif option == "5. Top 10 Most Popular Movies":
        df = pd.read_sql_query(
            """
            SELECT
                title,
                popularity,
                vote_average,
                vote_count
            FROM movies
            ORDER BY popularity DESC
            LIMIT 10
            """,
            conn
        )

    elif option == "6. Directors with More Than 3 Movies":
        df = pd.read_sql_query(
            """
            SELECT
                c.person_name AS director_name,
                COUNT(DISTINCT c.movie_id) AS movie_count
            FROM crew c
            WHERE LOWER(c.job) = 'director'
              AND c.person_name IS NOT NULL
            GROUP BY c.person_id, c.person_name
            HAVING COUNT(DISTINCT c.movie_id) > 3
            ORDER BY movie_count DESC
            """,
            conn
        )

    elif option == "7. Top 10 Actors by Movie Count":
        df = pd.read_sql_query(
            """
            SELECT
                c.actor_name,
                COUNT(DISTINCT c.movie_id) AS movie_count
            FROM cast c
            WHERE c.actor_name IS NOT NULL
            GROUP BY c.person_id, c.actor_name
            ORDER BY movie_count DESC
            LIMIT 10
            """,
            conn
        )

    elif option == "8. Movies with Profit Greater Than Average Profit":
        df = pd.read_sql_query(
            """
            SELECT
                title,
                budget,
                revenue,
                profit
            FROM movies
            WHERE budget > 0
              AND revenue > 0
              AND profit > (
                  SELECT AVG(profit)
                  FROM movies
                  WHERE budget > 0
                    AND revenue > 0
              )
            ORDER BY profit DESC
            """,
            conn
        )

    elif option == "9. Genres with Average Rating Above 7":
        df = pd.read_sql_query(
            """
            SELECT
                g.genre_name,
                ROUND(AVG(m.vote_average), 2) AS average_rating,
                COUNT(DISTINCT m.movie_id) AS movie_count
            FROM movies m
            JOIN movie_genres mg
                ON m.movie_id = mg.movie_id
            JOIN genres g
                ON mg.genre_id = g.genre_id
            GROUP BY g.genre_id, g.genre_name
            HAVING AVG(m.vote_average) > 7
            ORDER BY average_rating DESC
            """,
            conn
        )

    elif option == "10. Movies Released Per Year":
        df = pd.read_sql_query(
            """
            SELECT
                release_year,
                COUNT(*) AS movie_count
            FROM movies
            GROUP BY release_year
            ORDER BY release_year
            """,
            conn
        )

    st.subheader("📊 Query Results")
    st.write("Selected query:", option)
    st.dataframe(df, use_container_width=True)





