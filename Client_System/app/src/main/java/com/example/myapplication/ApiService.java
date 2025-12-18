package com.example.myapplication;

import java.util.List;
import retrofit2.Call;
import retrofit2.http.GET;

public interface ApiService {
    // 서버 views.py의 GET 함수와 매칭
    // 주소 예시: http://IP:8000/api/detect/
    @GET("api/detect/")
    Call<List<Detection>> getDetections();
}