from functools import lru_cache

# Application Use Cases
from application.use_cases.channels.create.create_channel_use_case import CreateChannelUseCase
from application.use_cases.channels.get_all.list_channels_use_case import ListChannelsUseCase
from application.use_cases.channels.update.update_channel_use_case import UpdateChannelUseCase
from application.use_cases.channels.delete.delete_channel_use_case import DeleteChannelUseCase
from application.use_cases.hello.get.get_hello_use_case import GetHelloUseCase
from application.use_cases.health.health_use_case import HealthUseCase
from application.use_cases.print_jobs.create.create_print_job_use_case import CreatePrintJobUseCase
from application.use_cases.print_jobs.get_all.list_print_jobs_use_case import ListPrintJobsUseCase
from application.use_cases.printer.discover.discover_printer_use_case import DiscoverPrinterUseCase
from application.use_cases.printer.get_one_status_by_name.get_one_status_by_name_use_case import GetOneStatusByNameUseCase
from application.use_cases.printer.get_status.get_status_use_case import GetStatusUseCase
from application.use_cases.printer.get_all.list_printers_use_case import ListPrintersUseCase
from application.use_cases.printer.create.create_printer_use_case import CreatePrinterUseCase
from application.use_cases.printer.update.update_printer_use_case import UpdatePrinterUseCase
from application.use_cases.printer.delete.delete_printer_use_case import DeletePrinterUseCase
from application.use_cases.template.get_all.list_templates_use_case import ListTemplatesUseCase
from application.use_cases.template.preview_label.preview_label_use_case import PreviewLabelUseCase
from application.use_cases.template.preview_remito.preview_remito_use_case import PreviewRemitoUseCase
from application.use_cases.printer.test.test_printer_use_case import TestPrinterUseCase

# Infrastructure Controllers
from infrastructure.controllers.hello.hello_get_controller import HelloGetController
from infrastructure.controllers.health.health_controller import HealthController
from infrastructure.controllers.channels.create.create_channel_controller import CreateChannelController
from infrastructure.controllers.channels.get_all.list_channels_controller import ListChannelsController
from infrastructure.controllers.channels.update.update_channel_controller import UpdateChannelController
from infrastructure.controllers.channels.delete.delete_channel_controller import DeleteChannelController
from infrastructure.controllers.print_jobs.create.create_print_job_controller import CreatePrintJobController
from infrastructure.controllers.print_jobs.get_all.list_print_jobs_controller import ListPrintJobsController
from infrastructure.controllers.printer.discover.discover_printer_controller import DiscoverPrinterController
from infrastructure.controllers.printer.get_one_status_by_name.get_one_status_by_name_controller import GetOneStatusByNameController
from infrastructure.controllers.printer.get_status.get_status_controller import GetStatusController
from infrastructure.controllers.printer.get_all.list_printers_controller import ListPrintersController
from infrastructure.controllers.printer.create.create_printer_controller import CreatePrinterController
from infrastructure.controllers.printer.update.update_printer_controller import UpdatePrinterController
from infrastructure.controllers.printer.delete.delete_printer_controller import DeletePrinterController
from infrastructure.controllers.template.get_all.list_templates_controller import ListTemplatesController
from infrastructure.controllers.template.label_preview.preview_label_controller import PreviewLabelController
from infrastructure.controllers.template.remito_preview.preview_remito_controller import PreviewRemitoController
from infrastructure.controllers.printer.test.test_printer_controller import TestPrinterController

# Infrastructure Services
from infrastructure.services.printer_discovery_service import CupsPrinterDiscoveryService

# Repositories (Infrastructure implementations)
from infrastructure.repositories.printer_repository import PrinterRepository
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.repositories.template_repository import TemplateRepository
from infrastructure.repositories.print_job_repository import PrintJobRepository

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

    # Channel - Create
    @lru_cache
    def init_create_channel_controller(self) -> CreateChannelController:
        from infrastructure.db.database import engine
        repo = ChannelRepository(engine)
        use_case = CreateChannelUseCase(repo)
        return CreateChannelController(use_case)

    def create_channel_controller(self) -> CreateChannelController:
        return self.init_create_channel_controller()

    # Channel - List
    @lru_cache
    def init_list_channels_controller(self) -> ListChannelsController:
        from infrastructure.db.database import engine
        channel_repo = ChannelRepository(engine)
        template_repo = TemplateRepository(engine)
        use_case = ListChannelsUseCase(channel_repo, template_repo)
        return ListChannelsController(use_case)

    def list_channels_controller(self) -> ListChannelsController:
        return self.init_list_channels_controller()

    # Channel - Update
    @lru_cache
    def init_update_channel_controller(self) -> UpdateChannelController:
        from infrastructure.db.database import engine
        repo = ChannelRepository(engine)
        use_case = UpdateChannelUseCase(repo)
        return UpdateChannelController(use_case)

    def update_channel_controller(self) -> UpdateChannelController:
        return self.init_update_channel_controller()

    # Channel - Delete
    @lru_cache
    def init_delete_channel_controller(self) -> DeleteChannelController:
        from infrastructure.db.database import engine
        repo = ChannelRepository(engine)
        use_case = DeleteChannelUseCase(repo)
        return DeleteChannelController(use_case)

    def delete_channel_controller(self) -> DeleteChannelController:
        return self.init_delete_channel_controller()

    # PrintJob - Create
    @lru_cache
    def init_create_print_job_controller(self) -> CreatePrintJobController:
        from infrastructure.db.database import engine
        repo = PrintJobRepository(engine)
        use_case = CreatePrintJobUseCase(repo)
        return CreatePrintJobController(use_case)

    def create_print_job_controller(self) -> CreatePrintJobController:
        return self.init_create_print_job_controller()

    # PrintJob - List
    @lru_cache
    def init_list_print_jobs_controller(self) -> ListPrintJobsController:
        from infrastructure.db.database import engine
        repo = PrintJobRepository(engine)
        use_case = ListPrintJobsUseCase(repo)
        return ListPrintJobsController(use_case)

    def list_print_jobs_controller(self) -> ListPrintJobsController:
        return self.init_list_print_jobs_controller()

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

    # Printer - List
    @lru_cache
    def init_list_printers_controller(self) -> ListPrintersController:
        from infrastructure.db.database import engine
        repo = PrinterRepository(engine)
        use_case = ListPrintersUseCase(repo)
        return ListPrintersController(use_case)

    def list_printers_controller(self) -> ListPrintersController:
        return self.init_list_printers_controller()

    # Printer - Create
    @lru_cache
    def init_create_printer_controller(self) -> CreatePrinterController:
        from infrastructure.db.database import engine
        repo = PrinterRepository(engine)
        use_case = CreatePrinterUseCase(repo)
        return CreatePrinterController(use_case)

    def create_printer_controller(self) -> CreatePrinterController:
        return self.init_create_printer_controller()

    # Printer - Update
    @lru_cache
    def init_update_printer_controller(self) -> UpdatePrinterController:
        from infrastructure.db.database import engine
        repo = PrinterRepository(engine)
        use_case = UpdatePrinterUseCase(repo)
        return UpdatePrinterController(use_case)

    def update_printer_controller(self) -> UpdatePrinterController:
        return self.init_update_printer_controller()

    # Printer - Delete
    @lru_cache
    def init_delete_printer_controller(self) -> DeletePrinterController:
        from infrastructure.db.database import engine
        repo = PrinterRepository(engine)
        use_case = DeletePrinterUseCase(repo)
        return DeletePrinterController(use_case)

    def delete_printer_controller(self) -> DeletePrinterController:
        return self.init_delete_printer_controller()

    # Template - List
    @lru_cache
    def init_list_templates_controller(self) -> ListTemplatesController:
        from infrastructure.db.database import engine
        repo = TemplateRepository(engine)
        use_case = ListTemplatesUseCase(repo)
        return ListTemplatesController(use_case)

    def list_templates_controller(self) -> ListTemplatesController:
        return self.init_list_templates_controller()

    # Template - Label Preview
    @lru_cache
    def init_preview_label_controller(self) -> PreviewLabelController:
        from domain.services.label_template_service import LabelTemplateService
        from domain.services.label_render_service import PlaceholderLabelRenderer
        from domain.services.label_template_resolver import LegacyLabelTemplateResolver
        from infrastructure.db.database import engine
        
        channel_repo = ChannelRepository(engine)
        template_repo = TemplateRepository(engine)
        
        template_service = LabelTemplateService(
            resolver=LegacyLabelTemplateResolver(),
            renderer=PlaceholderLabelRenderer()
        )
        use_case = PreviewLabelUseCase(
            template_service=template_service,
            channel_repo=channel_repo,
            template_repo=template_repo
        )
        return PreviewLabelController(use_case)

    def preview_label_controller(self) -> PreviewLabelController:
        return self.init_preview_label_controller()

    # Template - Remito Preview
    @lru_cache
    def init_remito_preview_controller(self) -> PreviewRemitoController:
        from domain.services.remito_template_service import RemitoTemplateService
        from infrastructure.services.barcode_service import BarcodeService
        from domain.services.remito_render_service import PlaceholderRemitoRenderer
        from domain.services.remito_template_resolver import LegacyRemitoTemplateResolver
        from infrastructure.db.database import engine
        
        channel_repo = ChannelRepository(engine)
        template_repo = TemplateRepository(engine)
        
        try:
            from infrastructure.html_remito_render_service import HtmlRemitoRenderer
            barcode_service = BarcodeService()
            renderer = HtmlRemitoRenderer(barcode_service)
        except ImportError:
            renderer = PlaceholderRemitoRenderer()
            
        template_service = RemitoTemplateService(
            renderer=renderer,
            resolver=LegacyRemitoTemplateResolver(),
        )
        use_case = PreviewRemitoUseCase(
            template_service=template_service,
            channel_repo=channel_repo,
            template_repo=template_repo
        )
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
