import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import plotly.graph_objects as go
import plotly.express as px

# Конфигурация страницы
st.set_page_config(
    page_title="ML Сравнение: Линейная регрессия vs Случайный лес",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стили
st.markdown("""
    <style>
    .main {
        padding-top: 0rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-card-forest {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    h1 {
        color: #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown("# 📊 Линейная регрессия vs Случайный лес")
st.markdown("### Интерактивное сравнение моделей с возможностью загрузки своих данных")

# Боковая панель
st.sidebar.title("⚙️ Управление")
show_explanation = st.sidebar.checkbox("👁️ Показать объяснения", value=True, key="show_explanation")

# Выбор источника данных
data_source = st.sidebar.radio(
    "📁 Источник данных:",
    ("Встроенные датасеты", "Загрузить CSV файл"),
    key="data_source"
)

# Переменная для хранения данных
df = None
X = None
y = None

if data_source == "Встроенные датасеты":
    # ============== ВСТРОЕННЫЕ ДАТАСЕТЫ ==============
    dataset_choice = st.sidebar.selectbox(
        "Выбери датасет:",
        ("Простые линейные данные", "Сложные нелинейные данные", "Данные с выбросами", "Множество признаков"),
        key="dataset_choice"
    )

    if dataset_choice == "Простые линейные данные":
        np.random.seed(42)
        X = np.linspace(0, 10, 80).reshape(-1, 1)
        noise = np.random.normal(0, 1, 80)
        y = 2 * X.flatten() + 5 + noise
        dataset_name = "Простые линейные данные"
        dataset_desc = "Линейная зависимость между оценками и зарплатой"
        expected_winner = "linear"
        explanation = {
            "why": "Данные имеют четко выраженную линейную зависимость.",
            "linear": "✅ Идеально подходит — может найти прямую линию.",
            "forest": "❌ Переусложняет задачу для простых линейных данных.",
            "insight": "💡 Когда данные действительно линейны, усложнение модели не помогает."
        }

    elif dataset_choice == "Сложные нелинейные данные":
        np.random.seed(42)
        X = np.linspace(0, 10, 100).reshape(-1, 1)
        noise = np.random.normal(0, 1.5, 100)
        y = ((X.flatten() - 5) / 2) ** 2 + 2 + noise
        dataset_name = "Сложные нелинейные данные"
        dataset_desc = "U-образная кривая (например, стоимость доставки)"
        expected_winner = "forest"
        explanation = {
            "why": "Данные имеют явно нелинейную, U-образную форму.",
            "linear": "❌ Пытается провести прямую через U-образные данные.",
            "forest": "✅ Отлично аппроксимирует кривую через множество деревьев.",
            "insight": "💡 Многие реальные зависимости нелинейны — лес справляется лучше."
        }

    elif dataset_choice == "Данные с выбросами":
        np.random.seed(42)
        X = np.linspace(0, 10, 100).reshape(-1, 1)
        noise = np.random.normal(0, 1, 100)
        y = 1.5 * X.flatten() + 3 + noise
        # Добавляем выбросы
        outlier_indices = np.random.choice(100, 15, replace=False)
        y[outlier_indices] += np.random.choice([-12, 15], 15)
        dataset_name = "Данные с выбросами"
        dataset_desc = "Несколько аномальных значений среди нормальных"
        expected_winner = "forest"
        explanation = {
            "why": "Данные содержат аномальные значения (выбросы).",
            "linear": "❌ Даже один выброс может сильно сдвинуть линию.",
            "forest": "✅ Благодаря множеству деревьев, выбросы имеют меньшее влияние.",
            "insight": "💡 Случайный лес обладает встроенной устойчивостью к грязным данным."
        }

    else:  # Множество признаков
        np.random.seed(42)
        X = np.linspace(0, 10, 120).reshape(-1, 1)
        noise = np.random.normal(0, 2, 120)
        y = 2 * X.flatten() + np.sin(X.flatten() * 1.5) * 4 + (X.flatten() / 10) ** 1.5 * 6 + noise
        dataset_name = "Множество признаков"
        dataset_desc = "Комплексная зависимость от нескольких факторов"
        expected_winner = "forest"
        explanation = {
            "why": "Реальные данные часто зависят от множества взаимодействующих факторов.",
            "linear": "❌ Может захватить только общий тренд.",
            "forest": "✅ Каждое дерево выбирает разные подмножества признаков.",
            "insight": "💡 В сложных данных случайный лес часто становится лучшим выбором."
        }

else:
    # ============== ЗАГРУЗКА CSV ==============
    st.sidebar.markdown("### 📤 Загрузи CSV файл")
    uploaded_file = st.sidebar.file_uploader("Выбери CSV файл", type=['csv'], key="csv_uploader")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success("✅ Файл загружен успешно!")
            
            st.sidebar.markdown("### Выбери колонки")
            cols = df.columns.tolist()
            
            x_col = st.sidebar.selectbox("Независимая переменная (X):", cols, key="x_col")
            y_col = st.sidebar.selectbox("Зависимая переменная (Y):", cols, key="y_col")
            
            if x_col and y_col:
                X = df[[x_col]].values
                y = df[y_col].values
                
                dataset_name = "Загруженные данные из CSV"
                dataset_desc = f"X: {x_col}, Y: {y_col}"
                expected_winner = "forest"  # По умолчанию
                explanation = {
                    "why": "Это твои пользовательские данные.",
                    "linear": "Может быть хороша для простых линейных зависимостей.",
                    "forest": "Может лучше справиться со сложными паттернами.",
                    "insight": "💡 Посмотри на графики и метрики, чтобы выбрать лучшую модель."
                }
                
                st.sidebar.markdown("---")
                st.sidebar.info(f"📊 Загружено {len(df)} строк")
                
        except Exception as e:
            st.sidebar.error(f"❌ Ошибка при загрузке: {str(e)}")

# ============== ОСНОВНОЙ КОНТЕНТ ==============

if X is not None and y is not None:
    
    # Показываем информацию о датасете
    if show_explanation:
        st.markdown("---")
        st.markdown("### 📚 О этом датасете")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**📌 Описание:**\n{dataset_desc}")
        
        with col2:
            st.success(f"**✅ Линейная регрессия:**\n\n{explanation['linear']}")
        
        with col3:
            st.warning(f"**🌳 Случайный лес:**\n\n{explanation['forest']}")
        
        st.markdown(f"**{explanation['insight']}**")
    
    st.markdown("---")
    
    # ============== ОБУЧЕНИЕ МОДЕЛЕЙ ==============
    
    # Линейная регрессия
    linear_model = LinearRegression()
    linear_model.fit(X, y)
    y_pred_linear = linear_model.predict(X)
    
    # Случайный лес
    forest_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    forest_model.fit(X, y)
    y_pred_forest = forest_model.predict(X)
    
    # Расчет метрик
    def calculate_metrics(y_true, y_pred):
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        return {
            'MSE': mse,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        }
    
    linear_metrics = calculate_metrics(y, y_pred_linear)
    forest_metrics = calculate_metrics(y, y_pred_forest)
    
    # ============== ГРАФИК ==============
    st.markdown("### 📈 Визуализация предсказаний")
    
    fig = go.Figure()
    
    # Сортируем по X для красивых линий
    sorted_indices = np.argsort(X.flatten())
    X_sorted = X[sorted_indices]
    y_pred_linear_sorted = y_pred_linear[sorted_indices]
    y_pred_forest_sorted = y_pred_forest[sorted_indices]
    
    # Фактические данные
    fig.add_trace(go.Scatter(
        x=X.flatten(),
        y=y,
        mode='markers',
        name='Фактические данные',
        marker=dict(size=8, color='#10b981', opacity=0.7),
        hovertemplate='<b>Фактические данные</b><br>X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>'
    ))
    
    # Линейная регрессия
    fig.add_trace(go.Scatter(
        x=X_sorted.flatten(),
        y=y_pred_linear_sorted,
        mode='lines',
        name='Линейная регрессия',
        line=dict(color='#3b82f6', width=3),
        hovertemplate='<b>Линейная регрессия</b><br>X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>'
    ))
    
    # Случайный лес
    fig.add_trace(go.Scatter(
        x=X_sorted.flatten(),
        y=y_pred_forest_sorted,
        mode='lines',
        name='Случайный лес',
        line=dict(color='#f59e0b', width=3, dash='dash'),
        hovertemplate='<b>Случайный лес</b><br>X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Сравнение предсказаний моделей',
        xaxis_title='Признак (X)',
        yaxis_title='Результат (Y)',
        hovermode='closest',
        template='plotly_dark',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True, key="prediction_chart")
    
    st.info("💡 **Зелёные точки** — фактические данные. **Синяя линия** — предсказания Линейной регрессии. **Оранжевая пунктирная линия** — предсказания Случайного леса.")
    
    # ============== МЕТРИКИ ==============
    st.markdown("---")
    st.markdown("### 📊 Метрики качества")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**📌 Описание метрик:**")
        st.info("""
        **R² Score** — от 0 до 1. Ближе к 1 = лучше (0.9+ отлично).
        
        **RMSE** — корень из средней квадратичной ошибки, в тех же единицах что данные.
        
        **MAE** — средняя абсолютная ошибка. Чем меньше, тем лучше.
        """)
    
    with col2:
        st.markdown("**📊 Линейная регрессия**")
        st.metric("R² Score", f"{linear_metrics['R2']:.3f}", "")
        st.metric("RMSE", f"{linear_metrics['RMSE']:.3f}", "")
        st.metric("MAE", f"{linear_metrics['MAE']:.3f}", "")
    
    with col3:
        st.markdown("**🌳 Случайный лес**")
        st.metric("R² Score", f"{forest_metrics['R2']:.3f}", "")
        st.metric("RMSE", f"{forest_metrics['RMSE']:.3f}", "")
        st.metric("MAE", f"{forest_metrics['MAE']:.3f}", "")
    
    with col4:
        winner = "Линейная регрессия" if linear_metrics['R2'] > forest_metrics['R2'] else "Случайный лес"
        st.markdown(f"**🏆 Победитель:**")
        st.success(f"**{winner}**")
        st.metric("Разница R²", f"{abs(linear_metrics['R2'] - forest_metrics['R2']):.3f}", "")
    
    # ============== СРАВНЕНИЕ ХАРАКТЕРИСТИК ==============
    st.markdown("---")
    st.markdown("### ⚖️ Сравнение характеристик")
    
    characteristics = {
        'Интерпретируемость': {'Линейная': 95, 'Лес': 30},
        'Работа с нелинейностью': {'Линейная': 35, 'Лес': 95},
        'Устойчивость к выбросам': {'Линейная': 40, 'Лес': 92},
        'Скорость обучения': {'Линейная': 99, 'Лес': 70},
        'На маленьких данных': {'Линейная': 95, 'Лес': 60}
    }
    
    char_df = pd.DataFrame(characteristics).T
    
    fig_comparison = go.Figure()
    
    for col in char_df.columns:
        fig_comparison.add_trace(go.Bar(
            x=char_df.index,
            y=char_df[col],
            name=col,
            marker_color='#3b82f6' if col == 'Линейная' else '#f59e0b'
        ))
    
    fig_comparison.update_layout(
        title='Сравнение характеристик моделей',
        xaxis_title='Характеристика',
        yaxis_title='Оценка (0-100)',
        barmode='group',
        template='plotly_dark',
        height=400
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True, key="comparison_chart")
    
    # ============== ЗАКЛЮЧЕНИЕ ==============
    st.markdown("---")
    st.markdown("### 💡 Итоговый вывод")
    
    winner_model = "Линейная регрессия" if linear_metrics['R2'] > forest_metrics['R2'] else "Случайный лес"
    
    if winner_model == "Линейная регрессия":
        advice = """
        ✅ **Выбирай Линейную регрессию, когда:**
        - Данные действительно линейны или близки к линейности
        - Нужна максимальная интерпретируемость (понимать, почему модель так предсказывает)
        - Скорость и простота важнее чем точность
        - Мало данных для обучения
        - Нужна способность экстраполировать (предсказывать за пределами диапазона данных)
        """
    else:
        advice = """
        ✅ **Выбирай Случайный лес, когда:**
        - Данные сложные и нелинейные
        - В данных есть выбросы и аномалии
        - Точность предсказания критична
        - Интерпретируемость менее важна
        - Большой объем данных для обучения
        - Есть множество признаков и их взаимодействия
        """
    
    st.success(f"**Для этого датасета лучше работает: {winner_model}**\n\n{advice}")
    
    # ============== ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ==============
    st.markdown("---")
    st.markdown("### 📖 Дополнительная информация")
    
    with st.expander("📚 Что такое Линейная регрессия?"):
        st.markdown("""
        **Линейная регрессия** — это метод, который ищет прямую линию, которая лучше всего описывает зависимость между данными.
        
        **Основная формула:** `y = β₀ + β₁×x + ε`
        
        **Преимущества:**
        - Простая и понятная
        - Быстро обучается
        - Легко интерпретировать коэффициенты
        
        **Недостатки:**
        - Плохо работает с нелинейными данными
        - Чувствительна к выбросам
        - Требует выполнения определённых допущений
        """)
    
    with st.expander("🌳 Что такое Случайный лес?"):
        st.markdown("""
        **Случайный лес** — это ансамблевый метод, который использует множество деревьев решений и усредняет их предсказания.
        
        **Как работает:**
        1. Создаёт много деревьев решений на случайных подмножествах данных
        2. Каждое дерево использует случайный набор признаков
        3. Итоговое предсказание — среднее значение от всех деревьев
        
        **Преимущества:**
        - Отлично работает с нелинейными данными
        - Устойчив к выбросам и шуму
        - Высокая точность на сложных данных
        
        **Недостатки:**
        - Сложно интерпретировать ("чёрный ящик")
        - Медленнее обучается
        - Не может экстраполировать за пределы данных
        """)

else:
    st.warning("⚠️ Пожалуйста, загрузи CSV файл или выбери встроенный датасет для начала анализа.")

# ============== ВИДЕО ВНИЗУ ==============
st.markdown("---")
st.markdown("### 🎥 Демонстрационное видео")

try:
    st.video("video.mp4")
except Exception as e:
    st.info("ℹ️ Видео не добавлено. Вы можете загрузить video.mp4 в репозиторий для отображения демонстрации.")
