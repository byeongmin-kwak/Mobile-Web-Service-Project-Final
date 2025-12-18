package com.example.myapplication;

import android.content.Context;
import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class DetectionAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    // 뷰 타입 상수 정의 (0: 헤더, 1: 아이템)
    private static final int TYPE_HEADER = 0;
    private static final int TYPE_ITEM = 1;

    private List<Object> itemList; // Detection 객체와 String(날짜)이 섞인 리스트
    private Context context;

    public DetectionAdapter(Context context, List<Object> itemList) {
        this.context = context;
        this.itemList = itemList;
    }

    // 아이템이 헤더인지 실제 데이터인지 구별하는 함수
    @Override
    public int getItemViewType(int position) {
        if (itemList.get(position) instanceof String) {
            return TYPE_HEADER;
        } else {
            return TYPE_ITEM;
        }
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        if (viewType == TYPE_HEADER) {
            View view = LayoutInflater.from(context).inflate(R.layout.item_header, parent, false);
            return new HeaderViewHolder(view);
        } else {
            View view = LayoutInflater.from(context).inflate(R.layout.item_detection, parent, false);
            return new ItemViewHolder(view);
        }
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        if (holder instanceof HeaderViewHolder) {
            // [헤더 처리]
            String dateText = (String) itemList.get(position);
            ((HeaderViewHolder) holder).tvHeaderDate.setText(dateText);

        } else if (holder instanceof ItemViewHolder) {
            // [아이템 처리]
            Detection item = (Detection) itemList.get(position);
            ItemViewHolder itemHolder = (ItemViewHolder) holder;

            // 1. 퍼센트(%) 변환 (0.82 -> 82%)
            int percent = 0;
            try {
                percent = (int)(Float.parseFloat(item.confidence) * 100);
            } catch (Exception e) {}

            itemHolder.tvTitle.setText(item.label + "  " + percent + "%");

            // 색상 강조 (80% 이상 초록, 미만 주황)
            if (percent >= 80) itemHolder.tvTitle.setTextColor(Color.parseColor("#4CAF50"));
            else itemHolder.tvTitle.setTextColor(Color.parseColor("#FF5722"));

            // ================= [수정된 부분] 시간 포맷팅 =================
            try {
                // 1. 서버 날짜 문자열 정리 (예: "2025-12-17T15:31:54.123456")
                String rawDate = item.createdAt;

                // 소수점(.123456)이 있다면 제거해서 깔끔하게 만듦
                if (rawDate.contains(".")) {
                    rawDate = rawDate.split("\\.")[0];
                }

                // 2. 서버 포맷 파싱 ('T'가 있는 ISO 포맷)
                SimpleDateFormat serverFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault());
                Date date = serverFormat.parse(rawDate);

                // 3. 원하는 출력 포맷 (예: "11:30 AM")
                // Locale.US를 써야 "AM/PM"으로 나옵니다. (Locale.KOREA는 "오전/오후")
                SimpleDateFormat timeFormat = new SimpleDateFormat("h:mm a", Locale.US);
                itemHolder.tvTime.setText(timeFormat.format(date));

            } catch (Exception e) {
                // 에러 나면 그냥 T만 공백으로 바꿔서 보여줌
                itemHolder.tvTime.setText(item.createdAt.replace("T", " "));
            }
            // ==========================================================

            // 3. 이미지 로딩
            String fixedUrl = item.imageUrl;
            if (fixedUrl != null) {
                // 서버가 가끔 http 주소를 줄 때가 있어서, 강제로 https로 변경
//                if (fixedUrl.startsWith("http://")) {
//                    fixedUrl = fixedUrl.replace("http://", "https://");
//                }
            }

            android.util.Log.d("IMAGE_TEST", "이미지 주소: " + fixedUrl);

            Glide.with(context)
                    .load(fixedUrl)
                    .placeholder(R.mipmap.ic_launcher) // 로딩 중 보일 아이콘
                    .error(R.mipmap.ic_launcher)       // 에러 시 보일 아이콘
                    .into(itemHolder.ivImage);
        }
    }

    @Override
    public int getItemCount() {
        return itemList.size();
    }

    // 뷰홀더 클래스 2개 (헤더용, 아이템용)
    static class HeaderViewHolder extends RecyclerView.ViewHolder {
        TextView tvHeaderDate;
        public HeaderViewHolder(@NonNull View itemView) {
            super(itemView);
            tvHeaderDate = itemView.findViewById(R.id.tvHeaderDate);
        }
    }

    static class ItemViewHolder extends RecyclerView.ViewHolder {
        TextView tvTitle, tvTime;
        ImageView ivImage;
        public ItemViewHolder(@NonNull View itemView) {
            super(itemView);
            tvTitle = itemView.findViewById(R.id.tvTitle);
            tvTime = itemView.findViewById(R.id.tvTime);
            ivImage = itemView.findViewById(R.id.ivImage);
        }
    }
}