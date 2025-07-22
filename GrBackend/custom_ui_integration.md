# Web App with custom UI Integration Plan for Product Genie

## 1. Executive Summary

This document outlines a comprehensive plan to re-architect the Product Genie backend (`GrBackend`) to support a custom web-based User Interface (UI), moving away from the current Gradio-based interaction. The goal is to develop a professional, high-end, scalable, and secure application. This plan details the necessary backend re-development, the proposed new frontend architecture, and key considerations for system design, scalability, and security.

## 2. Current State Analysis

The existing `GrBackend` leverages Gradio for its user interface, tightly coupling the UI logic with the backend processing. The core functionalities include:
- LLM-based shot composition analysis (`LLM` class, using `GeminiLLMService`).
- Blender rendering integration (`BlenderRenderer` class).
- Google Sheets integration for prompt storage (`GSheetsService`).
- Basic authentication for Gradio in non-debug mode.

While Gradio provides rapid prototyping, it lacks the flexibility, customizability, and scalability required for a professional, high-end web application.

## 3. Proposed Architecture

The new architecture will adopt a clear separation of concerns, implementing a RESTful API backend and a modern JavaScript frontend application.

```
+-------------------+       +-------------------+       +-------------------+
|   User Browser    | <---> |   Frontend App    | <---> |   Backend API     |
| (Custom Web UI)   |       | (React/TypeScript)|       | (FastAPI/Python)  |
+-------------------+       +-------------------+       +-------------------+
         ^                                                       |
         |                                                       v
         |                                               +-------------------+
         |                                               |  LLM Service      |
         |                                               |  (Gemini, etc.)   |
         |                                               +-------------------+
         |                                                       |
         |                                                       v
         |                                               +-------------------+
         |                                               |  Blender Renderer |
         |                                               |  (External Process)|
         |                                               +-------------------+
         |                                                       |
         |                                                       v
         |                                               +-------------------+
         |                                               |  Google Sheets    |
         |                                               |  (Data Storage)   |
         +-------------------------------------------------------------------+
```

## 4. Backend Re-development (FastAPI)

The existing Python logic will be adapted to expose its functionalities via a RESTful API using FastAPI.

### 4.1. API Framework Selection: FastAPI

**Why FastAPI?**
- **Performance:** High performance, comparable to Node.js and Go.
- **Ease of Use:** Modern, intuitive, and easy to learn.
- **Asynchronous Support:** Built-in support for `async`/`await`, crucial for I/O-bound tasks like LLM calls and Blender rendering.
- **Data Validation:** Pydantic integration for robust request/response validation and serialization.
- **Automatic Documentation:** Generates OpenAPI (Swagger UI) and ReDoc documentation automatically, simplifying frontend integration and API maintenance.
- **Security Features:** Integrates well with OAuth2, JWT, and other security standards.

### 4.2. Core Backend Changes

1.  **Remove Gradio Dependencies:** Eliminate `gradio` imports and related UI logic from `app.py`.
2.  **FastAPI Application Setup:**
    -   Initialize a FastAPI application instance.
    -   Define API routes (`@app.post`, `@app.get`, etc.) for each required endpoint.
3.  **Endpoint Definition:**
    -   **`POST /generate-video`**:
        -   **Request Body:**
            -   `glb_file`: File upload (e.g., `UploadFile` from `fastapi.UploadFile`).
            -   `prompt`: String (scene description).
            -   `environment_color`: String (hex or rgba color).
        -   **Response:**
            -   `video_url`: URL to the generated video (e.g., hosted on cloud storage or served directly).
            -   `task_id`: (Optional, for async processing) A unique ID to track the video generation task.
        -   **Logic:** This endpoint will orchestrate the calls to `LLM.analyze_shot_composition`, `BlenderRenderer.render_video_from_glb`, and `GSheetsService.store_prompt_in_sheet`.
    -   **`GET /video-status/{task_id}`**: (If asynchronous processing is implemented)
        -   **Response:** Current status of the video generation task (e.g., "pending", "processing", "completed", "failed") and the `video_url` if completed.
    -   **`GET /health`**: Basic health check endpoint.
4.  **Data Models (Pydantic):**
    -   Define Pydantic models for request bodies and response payloads (e.g., `VideoGenerationRequest`, `VideoGenerationResponse`). This ensures strong typing and automatic validation.
5.  **Authentication and Authorization:**
    -   Implement a robust authentication mechanism. **OAuth2 with JWT (JSON Web Tokens)** is recommended for a professional web application.
    -   **User Registration/Login Endpoints:**
        -   `POST /register`: Register new users.
        -   `POST /token`: Authenticate users and issue JWTs.
    -   **Dependency Injection:** Use FastAPI's dependency injection system to protect endpoints, ensuring only authenticated and authorized users can access them.
    -   Store user credentials securely (e.g., hashed passwords).
6.  **Asynchronous Processing (Celery/Redis or FastAPI Background Tasks):**
    -   Video rendering can be a long-running process. To prevent blocking the API, implement asynchronous task processing.
    -   **Option 1 (Recommended for Scalability):** Celery with Redis/RabbitMQ as a message broker. The `/generate-video` endpoint would submit a task to Celery and immediately return a `task_id`. A separate worker process would handle the Blender rendering.
    -   **Option 2 (Simpler for initial MVP):** FastAPI's `BackgroundTasks`. This is suitable if the rendering time is acceptable within a single request lifecycle, but less scalable for heavy loads.
7.  **File Handling:**
    -   Securely handle uploaded GLB files. Store them temporarily on the server or directly upload to cloud storage (e.g., AWS S3, Google Cloud Storage) before passing the path to Blender.
    -   Manage generated video files: Store them in cloud storage and serve them via a CDN or signed URLs.
8.  **Error Handling:**
    -   Implement custom exception handlers for common errors (e.g., validation errors, file not found, LLM service errors).
    -   Return standardized JSON error responses.
9.  **Logging:**
    -   Integrate `loguru` (already in use) for comprehensive logging of API requests, responses, and internal processing.
10. **CORS (Cross-Origin Resource Sharing):**
    -   Configure CORS middleware in FastAPI to allow requests from the frontend domain.

## 5. New User UI Development (React with TypeScript)

A modern, responsive, and interactive web application will be built using a robust frontend framework.

### 5.1. Frontend Framework Selection: React with TypeScript

**Why React?**
- **Component-Based:** Promotes reusability and modularity.
- **Large Ecosystem:** Rich set of libraries and tools.
- **Community Support:** Extensive community and resources.
- **Performance:** Efficient DOM updates.
- **TypeScript:** Provides static typing, improving code quality, maintainability, and developer experience, especially for large applications.

### 5.2. Key Frontend Technologies

-   **Build Tool/Framework:**
    -   **Vite:** For fast development and optimized builds.
    -   **Next.js:** (Alternative) If Server-Side Rendering (SSR) or Static Site Generation (SSG) is required for SEO or initial load performance. For a high-end application, Next.js might be a strong contender.
-   **Styling:**
    -   **Tailwind CSS:** Utility-first CSS framework for rapid UI development and highly customizable designs.
    -   **Material-UI (MUI):** (Alternative) A comprehensive React UI library implementing Google's Material Design. Provides pre-built, high-quality components for a polished look.
-   **State Management:**
    -   **React Query (TanStack Query):** For efficient data fetching, caching, synchronization, and server state management. Reduces boilerplate for API interactions.
    -   **Zustand/Jotai:** (Alternative for client state) Lightweight and flexible state management libraries for local UI state.
-   **Routing:**
    -   **React Router:** Standard library for declarative routing in React applications.
-   **Form Management:**
    -   **React Hook Form:** For performant and flexible form validation.
-   **File Upload:**
    -   Use a library or native browser APIs for robust file uploads, potentially with progress indicators.

### 5.3. UI Components and Workflow

1.  **Login/Registration Pages:** Secure user authentication flow.
2.  **Dashboard/Main Page:**
    -   **GLB File Upload:** Drag-and-drop or file input component.
    -   **Prompt Input:** Text area for scene description.
    -   **Environment Color Picker:** Interactive color selection.
    -   **Generate Button:** Triggers the video generation API call.
    -   **Video Display Area:** Player for the generated video.
    -   **Progress/Status Indicator:** Show real-time status of video generation (if async).
3.  **User Profile/Settings:** (Optional, for future features)
4.  **Error/Success Notifications:** Toast messages or dedicated alert components.
5.  **Responsive Design:** Ensure the UI is fully responsive across various devices (desktop, tablet, mobile).
6.  **Accessibility:** Adhere to WCAG guidelines for an inclusive user experience.

## 6. Deployment and Hosting

### 6.1. Backend Deployment

-   **Cloud Provider:** AWS, Google Cloud Platform (GCP), or Azure.
-   **Deployment Strategy:**
    -   **Containerization (Docker):** Package the FastAPI application into a Docker image.
    -   **Orchestration:**
        -   **Kubernetes (EKS/GKE/AKS):** For highly scalable and resilient deployments.
        -   **AWS ECS/GCP Cloud Run:** Simpler container deployment options for managed services.
    -   **Serverless (AWS Lambda/GCP Cloud Functions with API Gateway):** (Alternative) If the application has infrequent usage patterns and can be broken down into smaller functions.
-   **Database:** If user data or persistent task status is needed, use a managed database service (e.g., AWS RDS, GCP Cloud SQL).
-   **Object Storage:** AWS S3, GCP Cloud Storage for storing GLB inputs and generated video outputs.
-   **CI/CD:** Automate deployment using GitHub Actions, GitLab CI/CD, or Jenkins.

### 6.2. Frontend Deployment

-   **Static Site Hosting:**
    -   **AWS S3 + CloudFront:** For high performance and global content delivery.
    -   **GCP Cloud Storage + Cloud CDN.**
    -   **Vercel/Netlify:** Excellent for Next.js/React applications, offering integrated CI/CD and global CDN.
-   **CI/CD:** Automate builds and deployments.

## 7. Scalability Considerations

-   **Backend:**
    -   **Stateless API:** Design API endpoints to be stateless for easier scaling.
    -   **Asynchronous Task Queues:** Decouple long-running tasks (Blender rendering) from the main API using Celery/Redis.
    -   **Load Balancing:** Distribute incoming requests across multiple backend instances.
    -   **Database Scaling:** Optimize queries, consider read replicas, sharding if necessary.
    -   **Caching:** Implement caching for frequently accessed data (e.g., LLM responses if applicable).
-   **Frontend:**
    -   **CDN:** Serve static assets (HTML, CSS, JS, images) from a Content Delivery Network for faster global delivery.
    -   **Code Splitting:** Load only necessary JavaScript bundles for each page/component.
    -   **Image Optimization:** Optimize and lazy-load images.

## 8. Security Best Practices

-   **HTTPS Everywhere:** Enforce SSL/TLS for all communication between frontend and backend.
-   **Authentication & Authorization:**
    -   Use strong, industry-standard authentication (JWT/OAuth2).
    -   Implement role-based access control (RBAC) if different user roles are introduced.
    -   Securely store user credentials (hashed passwords with strong salting).
-   **Input Validation:** Validate all user inputs on both frontend and backend to prevent injection attacks (XSS, SQL injection, command injection). FastAPI's Pydantic helps significantly here.
-   **File Upload Security:**
    -   Validate file types and sizes.
    -   Scan uploaded files for malware.
    -   Store files outside the web root.
-   **API Security:**
    -   Rate limiting to prevent abuse.
    -   CORS configuration to restrict access to authorized origins.
    -   Protect against CSRF (Cross-Site Request Forgery) if using cookie-based sessions (less common with JWT).
-   **Dependency Security:** Regularly update dependencies and scan for known vulnerabilities.
-   **Environment Variables:** Store sensitive configuration (API keys, database credentials) in environment variables, not directly in code.
-   **Logging and Monitoring:** Implement robust logging and monitoring to detect and respond to security incidents.

## 9. Development Workflow and Tools

-   **Version Control:** Git (GitHub/GitLab/Bitbucket).
-   **Code Quality:**
    -   **Backend:** Ruff (linting, formatting), MyPy (type checking).
    -   **Frontend:** ESLint (linting), Prettier (formatting), TypeScript (type checking).
-   **Testing:**
    -   **Backend:** Pytest (unit, integration tests).
    -   **Frontend:** Jest/React Testing Library (unit, integration tests), Cypress/Playwright (end-to-end tests).
-   **API Documentation:** FastAPI's auto-generated OpenAPI/Swagger UI.
-   **Project Management:** Jira, Trello, Asana, or similar.

## 10. Phased Implementation Plan (High-Level)

1.  **Phase 1: Backend API Development (MVP)**
    -   Set up FastAPI application.
    -   Migrate core `VideoProcessor` logic to API endpoints.
    -   Implement basic file upload and video generation endpoint.
    -   Implement basic authentication (e.g., API key for initial testing).
    -   Set up basic logging and error handling.
    -   Containerize the backend.
2.  **Phase 2: Frontend Development (MVP)**
    -   Set up React/TypeScript project.
    -   Develop core UI components: file upload, prompt input, color picker, generate button, video display.
    -   Integrate with the backend API.
    -   Implement basic UI validation and error display.
    -   Deploy frontend to static hosting.
3.  **Phase 3: Authentication & Security Enhancement**
    -   Implement full OAuth2/JWT authentication on the backend.
    -   Integrate authentication flow into the frontend.
    -   Add comprehensive input validation and error handling.
    -   Implement CORS.
4.  **Phase 4: Asynchronous Processing & Scalability**
    -   Integrate Celery/Redis for background video rendering tasks.
    -   Implement task status tracking endpoints.
    -   Optimize file storage (cloud storage).
    -   Implement basic caching.
5.  **Phase 5: UI/UX Refinement & Advanced Features**
    -   Enhance UI/UX with advanced styling (Tailwind/MUI).
    -   Add progress indicators, notifications.
    -   Implement responsive design.
    -   Explore additional features (e.g., user history, video gallery).
6.  **Phase 6: Monitoring, Logging & CI/CD**
    -   Set up comprehensive monitoring and alerting.
    -   Refine logging.
    -   Implement full CI/CD pipelines for both frontend and backend.

## 11. Pricing Assessment of Third-Party Services

This section provides a high-level assessment of potential costs associated with deploying and operating the Product Genie using the proposed architecture. Actual costs will vary significantly based on usage, specific service configurations, and chosen cloud provider.

### 11.0. Cost Summary Table (Estimated Monthly/Annual)

| Component                 | Estimated Cost (Low-End) | Estimated Cost (High-End) | Notes                                      |
| :------------------------ | :----------------------- | :------------------------ | :----------------------------------------- |
| **Cloud Hosting**         |                          |                           |                                            |
| Backend API (Compute)     | $10/month                | $50/month                 | Small VM or serverless container           |
| Blender Workers (GPU)     | $0.50/hour ($360/month)  | $5.00+/hour ($3600+/month)| Highly variable, depends on usage/GPU type |
| Object Storage (S3/GCS)   | $5/month                 | $50+/month                | Based on data volume and egress            |
| Database (RDS/Cloud SQL)  | $15/month                | $100/month                | If applicable, for user data               |
| Networking (Egress)       | Variable                 | High                      | Significant for high video streaming       |
| Load Balancer             | $15/month                | $30/month                 | Per load balancer                          |
| CDN (CloudFront/Cloud CDN)| $10/month                | $100+/month               | Based on data transfer and requests        |
| **Domain Registration**   | $10/year                 | $20/year                  | Annual cost                                |
| **Third-Party APIs**      |                          |                           |                                            |
| LLM Services (Gemini etc.)| $50/month                | $500+/month               | Per token/API call, highly usage-dependent |
| Google Sheets API         | Free Tier                | Minimal                   | Generous free tier                         |
| **Other Services**        |                          |                           |                                            |
| CI/CD (GitHub Actions)    | Free Tier                | $200+/month               | Based on build minutes                     |
| Monitoring & Logging      | $20/month                | $200+/month               | Based on data volume and features          |

*Note: All costs are estimates and can vary significantly based on actual usage, specific cloud provider, region, and service configurations. Blender rendering workers and LLM API usage are expected to be the primary cost drivers.*

### 11.0.1. Essential Costs for Proof-of-Concept (Low Users)

| Component                 | Estimated Cost (Monthly/Annual) | Notes                                      |
| :------------------------ | :------------------------------ | :----------------------------------------- |
| **Cloud Hosting**         |                                 |                                            |
| Backend API (Compute)     | $10 - $30/month                 | Smallest VM or serverless container        |
| Blender Workers (GPU)     | $0.50 - $1.00/hour (on-demand)  | Single, less powerful GPU instance, or serverless GPU for intermittent use |
| Object Storage (S3/GCS)   | $1 - $5/month                   | Minimal storage for GLB/video files        |
| Database (RDS/Cloud SQL)  | $15 - $50/month                 | Smallest instance for user data (if needed)|
| Networking (Egress)       | Low (usage-based)               | Minimal data transfer for few users        |
| **Domain Registration**   | $10 - $20/year                  | Annual cost                                |
| **Third-Party APIs**      |                                 |                                            |
| LLM Services (Gemini etc.)| $10 - $50/month                 | Low usage, potentially free tier           |
| Google Sheets API         | Free Tier                       | Generous free tier                         |
| **Other Services**        |                                 |                                            |
| CI/CD (GitHub Actions)    | Free Tier                       | Basic automation                           |
| Monitoring & Logging      | Free Tier - $10/month           | Basic cloud provider logging               |

*Note: This table focuses on the absolute essentials for a functional proof-of-concept with very low user traffic. Costs are highly dependent on actual usage and specific cloud provider choices. Blender rendering remains the most variable and potentially highest cost.*

### 11.1. Cloud Hosting (AWS/GCP/Azure)

The primary cloud hosting costs will stem from:

-   **Compute (Backend API & Workers):**
    -   **FastAPI Backend:** For a low-traffic application, a small virtual machine (e.g., AWS EC2 t3.micro/t3.small, GCP e2-micro/e2-small) or a serverless container service (e.g., AWS Fargate, GCP Cloud Run) could range from **$10 - $50 per month** for basic instances. As traffic scales, costs will increase with more instances or larger instance types.
    -   **Blender Rendering Workers (Critical Cost):** This is expected to be the most significant cost component due to the computational intensity of 3D rendering. Blender rendering benefits heavily from GPUs.
        -   **Dedicated GPU Instances:** Renting instances with powerful GPUs (e.g., AWS EC2 P/G instances, GCP A2/NVIDIA Tesla instances) can range from **$0.50 - $5.00+ per hour per instance**, depending on GPU type and region. For continuous operation or high demand, this can quickly escalate to **hundreds or thousands of dollars per month**.
        -   **Serverless GPU Options:** Some providers offer serverless GPU functions (e.g., AWS Lambda with GPU support, specialized rendering services), which can be cost-effective for intermittent workloads but might have cold start penalties.
        -   **Cost Optimization:** Implementing efficient rendering queues, optimizing Blender scenes, and potentially using spot instances (for non-critical, interruptible workloads) can help manage these costs.
-   **Storage (GLB Inputs, Video Outputs):**
    -   **Object Storage (AWS S3, GCP Cloud Storage):** Highly cost-effective for storing large amounts of data. Costs are typically based on storage volume and data transfer out. Expect **$5 - $50+ per month** depending on data volume and egress.
-   **Database (if applicable):**
    -   **Managed Database Service (AWS RDS, GCP Cloud SQL):** For user authentication data or task status. Small instances can start from **$15 - $100 per month**, scaling with data size and performance requirements.
-   **Networking:**
    -   **Data Transfer (Egress):** Data leaving the cloud provider's network is typically charged. This includes serving videos to users. Costs vary but can be a significant factor for high-traffic video streaming.
    -   **Load Balancers:** Essential for distributing traffic and ensuring high availability. Costs typically range from **$15 - $30 per month** per load balancer.
-   **Content Delivery Network (CDN - AWS CloudFront, GCP Cloud CDN):**
    -   For faster global delivery of frontend assets and generated videos. Costs are based on data transfer and requests. Can range from **$10 - $100+ per month** depending on usage.

### 11.2. Domain Registration

-   **Annual Cost:** Registering a custom domain name (e.g., `yourproductvideoservice.com`) typically costs between **$10 - $20 per year** from domain registrars like GoDaddy, Namecheap, Google Domains, etc.

### 11.3. Third-Party API Services

-   **LLM Services (Gemini, OpenAI, MistralAI):**
    -   These services are typically priced per token (input and output) or per API call. Costs can vary widely based on the volume of prompts and the complexity of the LLM responses.
    -   **Example:** Gemini API pricing (as of current knowledge) might be a few dollars per million tokens. For a high-volume application, this could range from **$50 - $500+ per month**, depending on the model used and usage. Many providers offer free tiers for initial usage.
-   **Google Sheets API:**
    -   Generally, the Google Sheets API has a generous free tier that should cover most typical usage for prompt storage. Very high volumes might incur minimal costs, but it's usually negligible compared to other services.

### 11.4. Other Services

-   **CI/CD (GitHub Actions, GitLab CI/CD):**
    -   Many CI/CD services offer free tiers for open-source projects or limited private usage. For larger teams or more extensive build minutes, costs can range from **$0 (free tier) to $50 - $200+ per month**.
-   **Monitoring & Logging (e.g., CloudWatch, Stackdriver, Datadog):**
    -   Basic logging and monitoring are often included with cloud providers. Advanced features, longer retention, or third-party services can add **$20 - $200+ per month** depending on data volume and features.

### 11.5. Summary of Cost Drivers

The most significant cost drivers for this application will be:

1.  **Blender Rendering Hardware:** The compute resources (especially GPUs) required for 3D rendering.
2.  **LLM API Usage:** The volume of interactions with the chosen Large Language Model.
3.  **Data Transfer (Egress):** Especially for serving generated video files to users.

It is crucial to monitor usage and optimize configurations to manage these costs effectively as the application scales.

## 12. Conclusion

This plan provides a robust roadmap for transforming the Product Genie into a professional, scalable, and secure web application with a custom UI. By leveraging modern technologies like FastAPI and React with TypeScript, we can achieve a high-quality product that meets the demands of a high-end application. The phased approach allows for iterative development and continuous delivery.

