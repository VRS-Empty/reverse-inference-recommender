# Reverse Inference Recommender

A Python project that simulates how modern recommendation systems (like TikTok, Instagram, Reddit, and News APIs) push content to users based on their profile, behavior, and social connections.  
This tool lets you create a character profile (age, gender, occupation, interests, etc.) and then generates recommendations using different algorithms such as collaborative filtering, content-based, demographic, popularity, hybrid, and social graph.

---

## Features

- **Character Builder**: Create a user profile with attributes such as age, gender, location, interests, personality traits, and more.
- **Multiple Algorithms**: Supports collaborative filtering, content-based, demographic-based, popularity/trending, hybrid, and social-graph recommendations.
- **Social Media Simulation**: Includes simulated clients for:
  - **Reddit** (interest-based posts)
  - **NewsAPI** (location and keyword-based news)
  - **TikTok** (trending and interest-based short videos)
  - **Instagram** (trending posts and interest-based content)
- **Interactive CLI**: Build a character, view recommendations, analyze results, and export them as JSON.
- **Detailed Analysis**: Includes breakdowns of average scores, source distributions, and popular hashtags.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/VRS-Empty/reverse-inference-recommender.git
cd reverse-inference-recommender
