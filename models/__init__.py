from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User, Role
from models.journalist import Journalist
from models.source import Source
from models.article import Article
from models.subscriber import Subscriber
from models.subscription_plan import SubscriptionPlan
from models.daily_summary import DailySummary
from models.activity_log import ActivityLog
from models.settings import Settings
from models.token_usage import TokenUsage
from models.fetch_statistics import FetchStatistics
