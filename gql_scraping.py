from datetime import datetime

import requests
import json
import time


SELLER_DOMAIN = "wardah-official"
TOKOPEDIA_GQL_ENDPOINT = "https://gql.tokopedia.com/"
REQUEST_HEADER = {
    "Content-Type": "application/json",
    "Origin": "https://www.tokopedia.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
}

seller_data = {}


try:
    seller_info_operation = [
        {
            "operationName": "ShopInfoCore",
            "variables": {
                "id": 0,
                "domain": SELLER_DOMAIN
            },
            "query": "query ShopInfoCore($id: Int!, $domain: String) {\n  shopInfoByID(input: {shopIDs: [$id], fields: [\"active_product\", \"address\", \"allow_manage_all\", \"assets\", \"core\", \"closed_info\", \"create_info\", \"favorite\", \"location\", \"status\", \"is_open\", \"other-goldos\", \"shipment\", \"shopstats\", \"shop-snippet\", \"other-shiploc\", \"shopHomeType\", \"branch-link\"], domain: $domain, source: \"shoppage\"}) {\n    result {\n      shopCore {\n        description\n        domain\n        shopID\n        name\n        tagLine\n        defaultSort\n        __typename\n      }\n      createInfo {\n        openSince\n        __typename\n      }\n      favoriteData {\n        totalFavorite\n        alreadyFavorited\n        __typename\n      }\n      activeProduct\n      shopAssets {\n        avatar\n        cover\n        __typename\n      }\n      location\n      isAllowManage\n      branchLinkDomain\n      isOpen\n      address {\n        name\n        id\n        email\n        phone\n        area\n        districtName\n        __typename\n      }\n      shipmentInfo {\n        isAvailable\n        image\n        name\n        product {\n          isAvailable\n          productName\n          uiHidden\n          __typename\n        }\n        __typename\n      }\n      shippingLoc {\n        districtName\n        cityName\n        __typename\n      }\n      shopStats {\n        productSold\n        totalTxSuccess\n        totalShowcase\n        __typename\n      }\n      statusInfo {\n        shopStatus\n        statusMessage\n        statusTitle\n        __typename\n      }\n      closedInfo {\n        closedNote\n        until\n        reason\n        __typename\n      }\n      bbInfo {\n        bbName\n        bbDesc\n        bbNameEN\n        bbDescEN\n        __typename\n      }\n      goldOS {\n        isGold\n        isGoldBadge\n        isOfficial\n        badge\n        shopTier\n        __typename\n      }\n      shopSnippetURL\n      customSEO {\n        title\n        description\n        bottomContent\n        __typename\n      }\n      __typename\n    }\n    error {\n      message\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
    ]

    seller_info_response = requests.request(
        "POST", TOKOPEDIA_GQL_ENDPOINT, json=seller_info_operation, headers=REQUEST_HEADER)
    seller_info_data = seller_info_response.json(
    )[0]["data"]["shopInfoByID"]["result"][0]["shopCore"]

    seller_data["domain"] = SELLER_DOMAIN
    seller_data["shop_id"] = seller_info_data["shopID"]
    seller_data["name"] = seller_info_data["name"]
    seller_data["tag_line"] = seller_info_data["tagLine"]

    seller_data["products"] = []

    print(
        f"[INFO] Getting products for seller {seller_data['name']} (Seller id : {seller_data['shop_id']})")

    current_product_page = 1

    while True:
        seller_products_operation = [
            {
                "operationName": "ShopProducts",
                "variables":
                {
                    "sid": seller_data["shop_id"],
                    "page": current_product_page,
                    "perPage": 80,
                    "etalaseId": "",
                    "sort": 1,
                    "user_districtId": "2274",
                    "user_cityId": "176",
                    "user_lat": "",
                    "user_long": ""
                },
                "query": "query ShopProducts($sid: String!, $page: Int, $perPage: Int, $keyword: String, $etalaseId: String, $sort: Int, $user_districtId: String, $user_cityId: String, $user_lat: String, $user_long: String) {\n  GetShopProduct(shopID: $sid, filter: {page: $page, perPage: $perPage, fkeyword: $keyword, fmenu: $etalaseId, sort: $sort, user_districtId: $user_districtId, user_cityId: $user_cityId, user_lat: $user_lat, user_long: $user_long}) {\n    status\n    errors\n    links {\n      prev\n      next\n      __typename\n    }\n    data {\n      name\n      product_url\n      product_id\n      price {\n        text_idr\n        __typename\n      }\n      primary_image {\n        original\n        thumbnail\n        resize300\n        __typename\n      }\n      flags {\n        isSold\n        isPreorder\n        isWholesale\n        isWishlist\n        __typename\n      }\n      campaign {\n        discounted_percentage\n        original_price_fmt\n        start_date\n        end_date\n        __typename\n      }\n      label {\n        color_hex\n        content\n        __typename\n      }\n      label_groups {\n        position\n        title\n        type\n        url\n        __typename\n      }\n      badge {\n        title\n        image_url\n        __typename\n      }\n      stats {\n        reviewCount\n        rating\n        __typename\n      }\n      category {\n        id\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
            }
        ]

        seller_products_response = requests.request(
            "POST", TOKOPEDIA_GQL_ENDPOINT, json=seller_products_operation, headers=REQUEST_HEADER)
        try:
            seller_products_data = seller_products_response.json()[
                0]["data"]["GetShopProduct"]["data"]
        except Exception as e:
            print("[ERROR] Stopping getting product links and reviews" + str(e))

            break

        if len(seller_products_data) == 0:
            print("[INFO] Reached beyond last page of seller products page")

        for product_data in seller_products_data:
            current_review_page = 1
            reviews = []

            while True:
                product_reviews_operation = [
                    {
                        "operationName": "ProductReviewListQueryV2",
                        "query": "query ProductReviewListQueryV2($productID: String!, $page: Int!, $perPage: Int!, $rating: Int!, $withAttachment: Int!) {\n  ProductReviewListQueryV2(productId: $productID, page: $page, perPage: $perPage, rating: $rating, withAttachment: $withAttachment) {\n    shop {\n      shopIdStr\n      name\n      image\n      url\n      __typename\n    }\n    list {\n      reviewIdStr\n      message\n      productRating\n      reviewCreateTime\n      reviewCreateTimestamp\n      isReportable\n      isAnonymous\n      imageAttachments {\n        attachmentId\n        imageUrl\n        imageThumbnailUrl\n        __typename\n      }\n      reviewResponse {\n        message\n        createTime\n        __typename\n      }\n      likeDislike {\n        totalLike\n        likeStatus\n        __typename\n      }\n      user {\n        userId\n        fullName\n        image\n        url\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
                        "variables": {
                            "page": current_review_page,
                            "rating": 0,
                            "withAttachment": 0,
                            "productID": product_data["product_id"],
                            "perPage": 10
                        }
                    }
                ]

                product_reviews_response = requests.request(
                    "POST", TOKOPEDIA_GQL_ENDPOINT, json=product_reviews_operation, headers=REQUEST_HEADER)
                product_reviews_data = product_reviews_response.json(
                )[0]["data"]["ProductReviewListQueryV2"]

                if len(product_reviews_data["list"]) == 0:
                    break

                for product_review in product_reviews_data["list"]:
                    reviews.append({
                        "review_id": product_review["reviewIdStr"],
                        "review": product_review["message"],
                        "rating": product_review["productRating"],
                        "time_posted": product_review["reviewCreateTimestamp"],
                        "num_of_attachments": len(product_review["imageAttachments"])
                    })

                current_review_page += 1

            print(
                f"[INFO] Product {product_data['name']} got {len(reviews)} reviews")

            seller_data["products"].append({
                "product_id": product_data["product_id"],
                "product_url": product_data["product_url"],
                "name": product_data["name"],
                "rating": product_data["stats"]["rating"],
                "review_count": product_data["stats"]["reviewCount"],
                "flags": product_data["flags"],
                "reviews": reviews
            })

        current_product_page += 1

except Exception as e:
    print("[ERROR] " + str(e))
finally:
    now = datetime.now()

    with open(f"data-{now.strftime('%d-%m-%Y-%H-%M-%S')}.json", "w") as data_file:
        json.dump(seller_data, data_file, indent=4)

    print("[WARN] Scrapping done!")
