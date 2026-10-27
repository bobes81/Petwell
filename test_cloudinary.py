"""Optional manual Cloudinary diagnostic. Never runs during test discovery."""

if __name__ == "__main__":
    import os

    import cloudinary

    if not all(
        os.environ.get(name)
        for name in (
            "CLOUDINARY_CLOUD_NAME",
            "CLOUDINARY_API_KEY",
            "CLOUDINARY_API_SECRET",
        )
    ):
        raise SystemExit(
            "Configure Cloudinary variables before running this optional diagnostic."
        )
    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
        secure=True,
    )
    raise SystemExit(
        "Use the authenticated blog image form to validate uploads with your own image. No upload performed."
    )
