package com.example.myapplication;

import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class MainActivity extends AppCompatActivity {

    // [중요] 에뮬레이터라면 "http://10.0.2.2:8000/"
    // [중요] 실제 폰이라면 PC IP "http://192.168.X.X:8000/"
//    private static final String BASE_URL = "https://byeongmin.pythonanywhere.com/";
    private static final String BASE_URL = "http://10.0.2.2:8000/";

    private RecyclerView recyclerView;
    private DetectionAdapter adapter;
    private SwipeRefreshLayout swipeRefreshLayout;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        recyclerView = findViewById(R.id.recyclerView);
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        swipeRefreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                // 당겼을 때 실행될 코드 -> 데이터 다시 불러오기
                fetchDataFromServer();
            }
        });

        fetchDataFromServer();
    }

    private void fetchDataFromServer() {
        // Retrofit 설정
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        ApiService apiService = retrofit.create(ApiService.class);

        // 서버로 GET 요청
        apiService.getDetections().enqueue(new Callback<List<Detection>>() {
            @Override
            public void onResponse(Call<List<Detection>> call, Response<List<Detection>> response) {
                swipeRefreshLayout.setRefreshing(false);

                if (response.isSuccessful() && response.body() != null) {
                    List<Detection> rawList = response.body();

                    // [데이터 가공 로직] : 원본 리스트 -> 헤더가 포함된 리스트로 변환
                    List<Object> groupedList = new ArrayList<>();
                    String lastDate = "";

                    for (Detection item : rawList) {
                        // 날짜 추출 (예: "2025-12-18")
                        // createdAt이 null이거나 짧을 경우를 대비한 안전 장치
                        String currentDate = "";
                        if(item.createdAt != null && item.createdAt.length() >= 10) {
                            currentDate = item.createdAt.substring(0, 10);
                        } else {
                            currentDate = "Unknown Date";
                        }

                        // 날짜가 바뀌면 헤더 추가
                        if (!currentDate.equals(lastDate)) {
                            groupedList.add(currentDate + " 감지 목록");
                            lastDate = currentDate;
                        }
                        groupedList.add(item); // 실제 데이터 추가
                    }

                    // 어댑터 연결 (Object 리스트 전달)
                    adapter = new DetectionAdapter(MainActivity.this, groupedList);
                    recyclerView.setAdapter(adapter);

                    // 로드 완료 메시지
                    Toast.makeText(MainActivity.this, "최신 데이터 불러오기 완료", Toast.LENGTH_SHORT).show();

                } else {
                    Log.e("API_ERROR", "응답 실패: " + response.code());
                    Toast.makeText(MainActivity.this, "서버 응답 실패", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<List<Detection>> call, Throwable t) {
                Log.e("API_ERROR", "통신 에러: " + t.getMessage());
                Toast.makeText(MainActivity.this, "서버 연결 실패. IP를 확인하세요.", Toast.LENGTH_LONG).show();
            }
        });
    }
}