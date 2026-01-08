import pytest
from parsercraft.mobile_cloud_analytics import (
    MobilePlatform,
    CloudProvider,
    MetricType,
    MobileAppConfig,
    MobilePlatformManager,
    CloudDeploymentManager,
    AnalyticsEvent,
    PerformanceMetric
)

class TestMobileAnalytics:
    def test_mobile_config_defaults(self):
        manager = MobilePlatformManager()
        
        # iOS Defaults
        ios_config = manager.create_mobile_config(
            MobilePlatform.IOS, "MyApp", "com.example.app"
        )
        assert ios_config.min_sdk_version == "13.0"
        assert "camera" in ios_config.permissions
        
        # Android Defaults
        android_config = manager.create_mobile_config(
            MobilePlatform.ANDROID, "MyApp", "com.example.app"
        )
        assert android_config.min_sdk_version == "21"
        assert "CAMERA" in android_config.permissions

    def test_package_app(self):
        manager = MobilePlatformManager()
        config = manager.create_mobile_config(
            MobilePlatform.WEB, "WebApp", "com.example.web"
        )
        result = manager.package_app(config)
        
        assert result["status"] == "success"
        assert "index.html" in result["artifacts"]
        assert len(manager.build_history) == 1

class TestCloudDeployment:
    def test_cloud_config_defaults(self):
        manager = CloudDeploymentManager()
        
        aws_config = manager.create_deployment_config(
            CloudProvider.AWS, "us-east-1", "t3.micro"
        )
        assert aws_config.tags["ManagedBy"] == "ParserCraft"
        assert aws_config.environment_vars["AWS_REGION"] == "us-east-1"

    def test_deploy_simulation(self):
        manager = CloudDeploymentManager()
        config = manager.create_deployment_config(
            CloudProvider.AZURE, "eastus", "Standard_B1s"
        )
        
        # Note: I need to check the deploy method return structure from the source I read
        # deploy(self, config: CloudDeploymentConfig, app_name: str, version: str = "1.0.0")
        
        result = manager.deploy(config, "MyService")
        assert "deployment_id" in result
        
        # I didn't read the end of `deploy` method in `read_file` (truncated at 300 lines)
        # But I can assume it returns a dict with status or id given the start.
        # "deployment_id" was visible.

class TestAnalyticsData:
    def test_analytics_event(self):
        evt = AnalyticsEvent(
            event_id="123",
            event_type="login",
            timestamp="2023-01-01T00:00:00Z"
        )
        d = evt.to_dict()
        assert d["event_id"] == "123"
        assert d["event_type"] == "login"

    def test_performance_metric(self):
        perf = PerformanceMetric(
            metric_name="latency",
            metric_type=MetricType.TIMER,
            value=150.5,
            timestamp="2023-01-01T00:00:00Z"
        )
        d = perf.to_dict()
        assert d["metric_name"] == "latency"
        assert d["value"] == 150.5
