# Social Media Virality Analyzer

## Overview

This application analyzes social media virality patterns using graph theory and the Disjoint Set Union (Union-Find) algorithm. It processes user interaction data to identify viral clusters and connected communities within social networks. Users can upload interaction data in CSV format or use sample data to visualize how content spreads through social networks. The system represents users as nodes and their interactions (likes, mentions, shares) as edges, then applies clustering algorithms to detect and visualize viral patterns.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
**Technology**: Streamlit web framework
- **Decision**: Streamlit chosen for rapid prototyping of data science applications
- **Rationale**: Provides built-in components for file uploads, data display, and interactive visualizations without requiring separate frontend/backend setup
- **Layout**: Wide layout configuration for better visualization space

### Data Processing Layer
**Components**:
1. **CSV Data Ingestion**: Pandas-based data loading supporting both uploaded files and sample data with flexible format detection
2. **Graph Construction**: NetworkX library for representing social network topology
3. **Cluster Detection**: Custom Union-Find (Disjoint Set Union) implementation

**Graph Model**:
- Nodes represent individual users
- Edges represent interactions between users (bidirectional relationships)
- **Flexible Input Format**: Accepts any CSV with at least 2 columns; automatically uses first two columns as user interaction pairs
- Column names are not required; internally renamed to `user_a` and `user_b` for processing

### Algorithm Implementation
**Union-Find Data Structure** (`union_find.py`):
- **Optimization**: Path compression in `find()` operation for O(α(n)) amortized time complexity
- **Union Strategy**: Union by rank to maintain balanced tree structure
- **Purpose**: Efficiently merge connected components and identify viral clusters
- **Interface**: Provides `find()`, `union()`, and `get_clusters()` methods

**Design Pattern**: The application follows a pipeline architecture:
1. Data ingestion → 2. Graph construction → 3. Cluster analysis → 4. Results export

### Data Validation
- **Flexible Format**: Accepts any CSV with at least 2 columns (no specific column names required)
- **Auto-detection**: Automatically uses first two columns as user interaction pairs
- **Data Cleaning**: Removes null values, trims whitespace, and filters out self-interactions
- Fallback to sample data when no file uploaded
- User-friendly error messages for invalid data formats

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework for data science
- **pandas**: CSV processing and data manipulation
- **networkx**: Graph data structure and algorithms

### Data Requirements
- **Input Format**: Any CSV file with at least 2 columns representing user interactions
- **Flexibility**: Column names don't matter; first two columns are automatically used
- **Sample Data**: `interactions.csv` included as reference dataset
- No external databases or APIs required - application operates on uploaded/local data only

### No External Services
This application runs entirely locally without external API integrations, authentication systems, or cloud services.