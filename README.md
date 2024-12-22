# API Documentation - Video Creative Generation and Scoring

## Overview

The **Video Creative Generation and Scoring API** automates the process of generating product advertisement videos based on input parameters and then grades them based on specific criteria. It combines multiple API services, including visual asset generation, script creation, audio synthesis, video assembly, and scoring, ensuring efficient and automated workflows.

---

## Endpoints

### 1. **Generate Video**
This endpoint generates a product advertisement video by integrating various media assets and synthesizing them into a cohesive video.

#### URL:
`POST http://localhost:8000/generate_video`

#### Request Body:

```json
{
  "video_request": {
    "video_details": {
      "product_name": "EcoVive Water Bottle",
      "tagline": "Stay Hydrated, Stay Green",
      "brand_palette": ["#00FF00", "#007700"],
      "dimensions": {
        "width": 1920,
        "height": 1080
      },
      "duration": 15,
      "cta_text": "Join the Movement. Shop Now!",
      "logo_url": "https://example.com/logo.png",
      "product_video_url": "https://example.com/product_video.mp4"
    }
  }
}
```

#### Response:

```json
{
  "status": "success",
  "video_url": "https://your-bucket-name.s3.your-region.amazonaws.com/videos/generated_video.mp4",
  "scoring": {
    "background_foreground_separation": 8,
    "brand_guideline_adherence": 9,
    "creativity_and_visual_appeal": 7,
    "product_focus": 10,
    "cta_effectiveness": 8,
    "audience_relevance": 9
  },
  "metadata": {
    "file_size": 1024000,
    "duration": 15,
    "dimensions": {
      "width": 1920,
      "height": 1080
    }
  }
}
```

**Explanation of the Response:**

- **status**: Indicates whether the video generation was successful.
- **video_url**: The URL of the generated video in the AWS S3 bucket.
- **scoring**: A set of numerical scores representing how well the video adheres to scoring criteria.
- **metadata**: Information about the generated video, including file size, duration, and dimensions.

---

### 2. **Grade Video**
This endpoint evaluates a given video based on specified criteria and returns a detailed grading report.

#### URL:
`POST http://localhost:8000/grade_video`

#### Request Body:

```json
{
  "file_url": "https://example.com/sample_video.mp4",
  "scoring_criteria": {
    "background_foreground_separation": 8,
    "brand_guideline_adherence": 9,
    "creativity_visual_appeal": 7,
    "product_focus": 10,
    "call_to_action": 8,
    "audience_relevance": 9
  }
}
```

#### Response:

```json
{
  "grading_response": {
    "background_foreground_separation": 8,
    "brand_guideline_adherence": 9,
    "creativity_and_visual_appeal": 7,
    "product_focus": 10,
    "cta_effectiveness": 8,
    "audience_relevance": 9
  }
}
```

**Explanation of the Response:**

- **grading_response**: The scoring results based on the grading criteria, with scores between 1 and 10 for each parameter.

---

## Scoring Criteria

- **background_foreground_separation**: Measures how well the background and foreground are separated for clarity.
- **brand_guideline_adherence**: Measures how well the video follows the brand’s visual guidelines.
- **creativity_and_visual_appeal**: The creativity and visual aesthetics of the video.
- **product_focus**: Evaluates how well the product is showcased in the video.
- **cta_effectiveness**: Assesses the effectiveness of the call to action in the video.
- **audience_relevance**: Evaluates the video’s relevance to the target audience.

---

## Local Setup

To set up the **Video Creative Generation and Scoring API** locally, follow these steps:

### Prerequisites:

1. **Python 3.7+**  
   Ensure that Python is installed on your system. You can download it from the official [Python website](https://www.python.org/downloads/).

2. **Install Dependencies**  
   Install the necessary Python libraries by running the following command:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up AWS S3**  
   The video generation output is stored in AWS S3, so ensure that you have an AWS account with access to S3. Create an S3 bucket and update the environment variables with the necessary credentials:

   - **AWS_ACCESS_KEY_ID**
   - **AWS_SECRET_ACCESS_KEY**
   - **AWS_S3_BUCKET_NAME**

4. **Set Up Gemini, Pexels, and Edge TTS APIs**  
   You'll need valid API keys for:
   - **Gemini API** for script generation and visual asset evaluation.
   - **Pexels API** for fetching stock images.
   - **Edge TTS** for converting text to speech.
   
   Store these API keys in environment variables.

### Running the API Server:

1. Clone the repository and navigate to the project directory:

   ```bash
   git clone https://github.com/your-username/video-creative-generation.git
   cd video-creative-generation
   ```

2. Set up the environment variables for your API keys and AWS credentials:

   ```bash
   export GEMINI_API_KEY="your-gemini-api-key"
   export PEXELS_API_KEY="your-pexels-api-key"
   export EDGE_TTS_API_KEY="your-edge-tts-api-key"
   export AWS_ACCESS_KEY_ID="your-aws-access-key"
   export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
   export AWS_S3_BUCKET_NAME="your-s3-bucket-name"
   ```

3. Start the FastAPI server:

   ```bash
   uvicorn app:app --reload
   ```

   This will start the server locally on port 8000.

### Testing the API:

Once the server is running, you can test the endpoints using a tool like **Postman** or **curl**.

- To generate a video, make a `POST` request to `http://localhost:8000/generate_video` with the JSON body as described above.
- To grade a video, make a `POST` request to `http://localhost:8000/grade_video` with the necessary parameters.

---

This markdown document includes:

- **API Endpoints**: Clear definitions of the video generation and grading APIs.
- **Scoring Criteria**: Explanation of each scoring criterion used to grade the video.
- **Local Setup**: Instructions for setting up and running the FastAPI server locally, including installation of dependencies and configuration of environment variables.