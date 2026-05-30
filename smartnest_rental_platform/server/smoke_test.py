import util


def main():
    util.load_saved_artifacts()

    rent_payload = {
        "size": 1000,
        "bhk": 2,
        "bathroom": 2,
        "city": "chennai",
        "area_type": "super area",
        "furnishing_status": "semi-furnished",
        "tenant_preferred": "bachelors",
    }
    rent = util.predict_rent(rent_payload)
    print("Rent prediction:", rent)

    scam_payload = {
        "rent": 12000,
        "size": 900,
        "bhk": 2,
        "bathroom": 2,
        "city": "chennai",
        "area_type": "super area",
        "furnishing_status": "semi-furnished",
        "tenant_preferred": "bachelors",
    }
    scam = util.predict_scam(scam_payload)
    print("Scam prediction:", scam)

    text = "2 bhk apartment, owner asks for advance before visit."
    text_result = util.verify_text(text)
    print("Text verification:", text_result)

    reco = util.recommend_listings(scam_payload, top_n=3)
    print("Recommendations:", reco[:1])

    locality = util.locality_analysis("chennai")
    print("Locality:", locality)


if __name__ == "__main__":
    main()
