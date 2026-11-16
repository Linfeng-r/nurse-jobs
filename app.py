#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读取 jobs.csv，用卡片展示招聘信息，标题在新标签页打开。"""

from __future__ import annotations

import csv
import html
from pathlib import Path

import streamlit as st

CSV_PATH = Path(__file__).resolve().with_name("jobs.csv")
COLUMNS = ["标题", "医院/单位名称", "发布日期", "所在地区", "链接"]


def load_jobs(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or []
        missing = [name for name in COLUMNS if name not in fieldnames]
        if missing:
            raise ValueError(
                f"{path.name} 缺少列：{', '.join(missing)}。"
                f"需要的表头是：{', '.join(COLUMNS)}。"
            )
        jobs: list[dict[str, str]] = []
        for row in reader:
            jobs.append({name: (row.get(name) or "").strip() for name in COLUMNS})
    return jobs


def matches(job: dict[str, str], query: str) -> bool:
    keyword = query.strip().casefold()
    if not keyword:
        return True
    haystack = " ".join(job[name] for name in COLUMNS if name != "链接")
    return keyword in haystack.casefold()


def render_card(job: dict[str, str]) -> None:
    title = html.escape(job["标题"] or "（无标题）")
    url = html.escape(job["链接"], quote=True)
    with st.container(border=True):
        if job["链接"]:
            st.markdown(
                (
                    f'<a href="{url}" target="_blank" rel="noopener noreferrer">'
                    f"<strong>{title}</strong></a>"
                ),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"**{job['标题'] or '（无标题）'}**")
        st.write(job["医院/单位名称"] or "医院/单位未知")
        date_col, region_col = st.columns(2)
        date_col.caption(f"发布日期：{job['发布日期'] or '未知'}")
        region_col.caption(f"所在地区：{job['所在地区'] or '未知'}")


def main() -> None:
    st.set_page_config(page_title="卫生人才招聘", page_icon="🏥", layout="centered")
    st.title("卫生人才招聘")
    st.caption("数据来自 jobs.csv。点击职位标题会在新标签页打开原链接。")

    try:
        jobs = load_jobs(CSV_PATH)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    if not jobs:
        st.warning(f"没有读到数据。请确认 {CSV_PATH.name} 与 app.py 在同一文件夹，并先运行 spider.py。")
        st.stop()

    query = st.text_input("搜索", placeholder="输入职位、医院、日期或地区")
    visible = [job for job in jobs if matches(job, query)]
    st.caption(f"显示 {len(visible)} / {len(jobs)} 条")

    if not visible:
        st.info("没有符合条件的职位。")
        return

    for job in visible:
        render_card(job)


if __name__ == "__main__":
    main()
