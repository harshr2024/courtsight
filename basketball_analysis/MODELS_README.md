# Model Files

The model files (`.pt` files) are too large for GitHub and have been excluded from the repository.

## Required Model Files

You need to place these model files in the `models/` directory:

- `models/player_detector.pt` (165 MB)
- `models/ball_detector_model.pt` (165 MB)
- `models/court_keypoint_detector.pt` (133 MB)

## Where to Get Models

1. **If you trained them yourself**: Use your trained model files
2. **If you have them locally**: Copy them from your local `models/` folder
3. **For deployment**: Upload models to cloud storage (S3, Google Drive, etc.) and download them during deployment setup

## Note for Deployment

When deploying to production:
- Store models in cloud storage (AWS S3, Google Cloud Storage, etc.)
- Download models during deployment/startup
- Or use a service like Hugging Face to host models

The models should remain in your local `models/` folder for local development.

