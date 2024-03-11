# de-reddit-reports


## Table of Contents
1. [About](#about)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [VM Setup Guide](#vm-setup-guide)

## About
**Powered by Mage-ai**
<div>
<img src="https://github.com/mage-ai/assets/blob/main/mascots/mascots-shorter.jpeg?raw=true">
</div>


The Data Engineering Reddit Data Dashboard provides a comprehensive view of key statistics from the Data Engineering's subreddit, encompassing both posts and comments over the past week. It features an in-depth analysis of sentiments expressed in these posts, comments, and by the authors themselves, all tracked and evaluated over the same seven-day period.

## Features

1. The project is hosted on the Google Cloud Platform 
2. Mage-ai is used for the orchestration of the ETL pipeline 
3. Data manipulation is done through the Spark cluster(Google dataproc), where by increasing the worker node, the workload can be distributed across and finished fster if needed.
4. The data transformation phase incorporates sentiment analysis on comments and posts to gauge the overall sentiment towards specific technologies or topics.
5. For data visualization, the project utilizes Google Data Studio to create graphical representations.

## Project Structure

<img src="./README_resources/de-reddit-reports-architecture.drawio (2).png" alt="project_structure" width="1200"/>

## VM Setup Guide
[Link to VM setup guide](./vm_setup.md)



