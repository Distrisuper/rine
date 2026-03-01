from functools import lru_cache

# Application Use Cases
from application.use_cases.channels.create.create_channel_use_case import CreateChannelUseCase
from application.use_cases.hello.get.get_hello_use_case import GetHelloUseCase
from application.use_cases.health.health_use_case import HealthUseCase
from application.use_cases.print_jobs.create.create_print_job_use_case import CreatePrintJobUseCase
from application.use_cases.printer.discover.discover_printer_use_case import DiscoverPrinterUseCase
from application.use_cases.printer.get_one_status_by_name.get_one_status_by_name_use_case import GetOneStatusByNameUseCase
from application.use_cases.printer.get_status.get_status_use_case import GetStatusUseCase
from application.use_cases.template.preview_label.preview_label_use_case import PreviewLabelUseCase
from application.use_cases.template.preview_remito.preview_remito_use_case import PreviewRemitoUseCase
from application.use_cases.printer.test.test_printer_use_case import TestPrinterUseCase

# Infrastructure Controllers
from infrastructure.controllers.hello.hello_get_controller import HelloGetController
from infrastructure.controllers.health.health_controller import HealthController
from infrastructure.controllers.channels.create.create_channel_controller import CreateChannelController
from infrastructure.controllers.print_jobs.create.create_print_job_controller import CreatePrintJobController
from infrastructure.controllers.printer.discover.discover_printer_controller import DiscoverPrinterController
from infrastructure.controllers.printer.get_one_status_by_name.get_one_status_by_name_controller import GetOneStatusByNameController
from infrastructure.controllers.printer.get_status.get_status_controller import GetStatusController
from infrastructure.controllers.template.label_preview.preview_label_controller import PreviewLabelController
from infrastructure.controllers.template.remito_preview.preview_remito_controller import PreviewRemitoController
from infrastructure.controllers.printer.test.test_printer_controller import TestPrinterController

# Infrastructure Services
from infrastructure.services.printer_discovery_service import CupsPrinterDiscoveryService

# Repositories
from domain.repositories.printer_repository import PrinterRepository
from domain.repositories.channel_repository import ChannelRepository
from domain.repositories.template_repository import TemplateRepository
from domain.repositories.print_job_repository import PrintJobRepository

class Container:
    # Hello
    @lru_cache
    def init_hello_controller(self) -> HelloGetController:
        use_case = GetHelloUseCase()
        return HelloGetController(use_case)

    def hello_controller(self) -> HelloGetController:
        return self.init_hello_controller()

    # Health
    @lru_cache
    def init_health_controller(self) -> HealthController:
        use_case = HealthUseCase()
        return HealthController(use_case)

    def health_controller(self) -> HealthController:
        return self.init_health_controller()

    # Channel
    @lru_cache
    def init_create_channel_controller(self) -> CreateChannelController:
        use_case = CreateChannelUseCase()
        return CreateChannelController(use_case)

    def create_channel_controller(self) -> CreateChannelController:
        return self.init_create_channel_controller()

    # PrintJob
    @lru_cache
    def init_create_print_job_controller(self) -> CreatePrintJobController:
        use_case = CreatePrintJobUseCase()
        return CreatePrintJobController(use_case)

    def create_print_job_controller(self) -> CreatePrintJobController:
        return self.init_create_print_job_controller()

    # Printer - Discover
    @lru_cache
    def init_discover_printer_controller(self) -> DiscoverPrinterController:
        discovery = CupsPrinterDiscoveryService()
        use_case = DiscoverPrinterUseCase(discovery)
        return DiscoverPrinterController(use_case)

    def discover_printer_controller(self) -> DiscoverPrinterController:
        return self.init_discover_printer_controller()

    # Printer - Get One Status By Name
    @lru_cache
    def init_get_one_status_by_name_controller(self) -> GetOneStatusByNameController:
        discovery = CupsPrinterDiscoveryService()
        use_case = GetOneStatusByNameUseCase(discovery)
        return GetOneStatusByNameController(use_case)

    def get_one_status_by_name_controller(self) -> GetOneStatusByNameController:
        return self.init_get_one_status_by_name_controller()

    # Printer - Get Status
    @lru_cache
    def init_get_status_controller(self) -> GetStatusController:
        discovery = CupsPrinterDiscoveryService()
        use_case = GetStatusUseCase(discovery)
        return GetStatusController(use_case)

    def get_status_controller(self) -> GetStatusController:
        return self.init_get_status_controller()

    # Template - Label Preview
    @lru_cache
    def init_preview_label_controller(self) -> PreviewLabelController:
        from domain.services.label_template_service import LabelTemplateService
        template_service = LabelTemplateService()
        use_case = PreviewLabelUseCase(template_service)
        return PreviewLabelController(use_case)

    def preview_label_controller(self) -> PreviewLabelController:
        return self.init_preview_label_controller()

    # Template - Remito Preview
    @lru_cache
    def init_remito_preview_controller(self) -> PreviewRemitoController:
        from domain.services.remito_template_service import RemitoTemplateService
        from infrastructure.services.barcode_service import BarcodeService
        from domain.services.remito_data_provider import InlineRemitoDataProvider
        from domain.services.remito_render_service import PlaceholderRemitoRenderer
        from domain.services.remito_template_resolver import LegacyRemitoTemplateResolver
        try:
            from infrastructure.html_remito_render_service import HtmlRemitoRenderer
            barcode_service = BarcodeService()
            renderer = HtmlRemitoRenderer(barcode_service)
        except ImportError:
            renderer = PlaceholderRemitoRenderer()
        template_service = RemitoTemplateService(
            renderer=renderer,
            resolver=LegacyRemitoTemplateResolver(),
            data_provider=InlineRemitoDataProvider(),
        )
        use_case = PreviewRemitoUseCase(template_service)
        return PreviewRemitoController(use_case)

    def remito_preview_controller(self) -> PreviewRemitoController:
        return self.init_remito_preview_controller()

    # Printer - Test
    @lru_cache
    def init_test_printer_controller(self) -> TestPrinterController:
        from infrastructure.db.database import engine
        printer_repo = PrinterRepository(engine)
        channel_repo = ChannelRepository(engine)
        template_repo = TemplateRepository(engine)
        print_job_repo = PrintJobRepository(engine)
        use_case = TestPrinterUseCase(
            printer_repo=printer_repo,
            channel_repo=channel_repo,
            template_repo=template_repo,
            print_job_repo=print_job_repo
        )
        return TestPrinterController(use_case)

    def test_printer_controller(self) -> TestPrinterController:
        return self.init_test_printer_controller()


container = Container()
