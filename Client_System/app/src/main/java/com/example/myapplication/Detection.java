package com.example.myapplication;

import com.google.gson.annotations.SerializedName;

public class Detection {
    @SerializedName("label")
    public String label;

    @SerializedName("confidence")
    public String confidence;

    @SerializedName("image") // 서버 Serializer가 주는 전체 URL
    public String imageUrl;

    @SerializedName("created_at")
    public String createdAt;
}