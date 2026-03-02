import os
import logging
from typing import Optional
from pathlib import Path
from functools import lru_cache

from sqlalchemy import create_engine
from sqlmodel import Session

# Repositories
from infrastructure.repositories.printer_repository import PrinterRepository
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.repositories.template_repository import TemplateRepository
from infrastructure.repositories.print_job_repository import PrintJobRepository

# Use Cases
from application.use_cases.printer.create.create_printer_use_case import CreatePrinterUseCase
from application.use_cases.printer.get_all.list_printers_use_case import ListPrintersUseCase
from application.use_cases.printer.get_status.get_status_use_case import GetStatusUseCase
from application.use_cases.printer.update.update_printer_use_case import UpdatePrinterUseCase
from application.use_cases.printer.delete.delete_printer_use_case import DeletePrinterUseCase
from application.use_cases.printer.discover.discover_printer_use_case import DiscoverPrinterUseCase
from application.use_cases.printer.get_one_status_by_name.get_one_status_by_name_use_case import GetOneStatusByNameUseCase
from application.use_cases.printer.print_test_page.print_test_page_use_case import PrintTestPageUseCase

from application.use_cases.channels.get_all.list_channels_use_case import ListChannelsUseCase
from application.use_cases.channels.create.create_channel_use_case import CreateChannelUseCase
from application.use_cases.channels.update.update_channel_use_case import UpdateChannelUseCase
from application.use_cases.channels.delete.delete_channel_use_case import DeleteChannelUseCase

from application.use_cases.template.get_all.list_templates_use_case import ListTemplatesUseCase
from application.use_cases.template.preview_label.preview_label_use_case import PreviewLabelUseCase
from application.use_cases.template.preview_remito.preview_remito_use_case import PreviewRemitoUseCase

from application.use_cases.print_jobs.get_all.list_print_jobs_use_case import ListPrintJobsUseCase
from application.use_cases.print_jobs.create.create_print_job_use_case import CreatePrintJobUseCase
from application.use_cases.print_jobs.print.print_job_use_case import PrintJobUseCase

from application.use_cases.health.health_use_case import HealthUseCase
from application.use_cases.example.get.get_example_use_case import GetExampleUseCase

# Controllers
from infrastructure.controllers.printer.create.create_printer_controller import CreatePrinterController
from infrastructure.controllers.printer.get_all.list_printers_controller import ListPrintersController
from infrastructure.controllers.printer.get_status.get_status_controller import GetStatusController
from infrastructure.controllers.printer.update.update_printer_controller import UpdatePrinterController
from infrastructure.controllers.printer.delete.delete_printer_controller import DeletePrinterController
from infrastructure.controllers.printer.discover.discover_printer_controller import DiscoverPrinterController
from infrastructure.controllers.printer.get_one_status_by_name.get_one_status_by_name_controller import GetOneStatusByNameController
from infrastructure.controllers.printer.print_test_page.print_test_page_controller import PrintTestPageController

from infrastructure.controllers.channels.get_all.list_channels_controller import ListChannelsController
from infrastructure.controllers.channels.create.create_channel_controller import CreateChannelController
from infrastructure.controllers.channels.update.update_channel_controller import UpdateChannelController
from infrastructure.controllers.channels.delete.delete_channel_controller import DeleteChannelController

from infrastructure.controllers.template.get_all.list_templates_controller import ListTemplatesController
from infrastructure.controllers.template.label_preview.preview_label_controller import PreviewLabelController
from infrastructure.controllers.template.remito_preview.preview_remito_controller import PreviewRemitoController

from infrastructure.controllers.print_jobs.get_all.list_print_jobs_controller import ListPrintJobsController
from infrastructure.controllers.print_jobs.create.create_print_job_controller import CreatePrintJobController
from infrastructure.controllers.print_jobs.print.print_job_controller import PrintJobController

from infrastructure.controllers.health.health_controller import HealthController
from infrastructure.controllers.example.example_get_controller import ExampleGetController

# Services
from infrastructure.services.printer_discovery_service import CupsPrinterDiscoveryService as PrinterDiscoveryService
from domain.services.label_template_service import LabelTemplateService
from infrastructure.services.zpl_label_render_service import ZplLabelRenderer
from domain.services.remito_template_service import RemitoTemplateService
from infrastructure.services.html_remito_render_service import HtmlRemitoRenderer
from infrastructure.services.barcode_service import BarcodeService

class Container:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL", "sqlite:///./rine.db")
        self.engine = create_engine(db_url)
        
        # Repositories (Shared)
        self._printer_repo = PrinterRepository(self.engine)
        self._channel_repo = ChannelRepository(self.engine)
        self._template_repo = TemplateRepository(self.engine)
        self._print_job_repo = PrintJobRepository(self.engine)
        
        # Services (Shared)
        self._printer_discovery_service = PrinterDiscoveryService()
        self._barcode_service = BarcodeService()
        
        # Label Services
        self._label_render_service = ZplLabelRenderer(templates_path="/app/infrastructure/templates/labels")
        self._label_template_service = LabelTemplateService(
            renderer=self._label_render_service
        )
        
        # Remito Services
        self._remito_render_service = HtmlRemitoRenderer(barcode_service=self._barcode_service)
        self._remito_template_service = RemitoTemplateService(
            renderer=self._remito_render_service
        )

    # --- Health Controller ---
    @lru_cache
    def init_health_controller(self) -> HealthController:
        use_case = HealthUseCase()
        return HealthController(use_case)

    def health_controller(self) -> HealthController:
        return self.init_health_controller()

    # --- Example Controller ---
    @lru_cache
    def init_example_controller(self) -> ExampleGetController:
        use_case = GetExampleUseCase()
        return ExampleGetController(use_case)

    def example_controller(self) -> ExampleGetController:
        return self.init_example_controller()

    # --- Printer Controllers ---
    
    @lru_cache
    def init_create_printer_controller(self) -> CreatePrinterController:
        use_case = CreatePrinterUseCase(self._printer_repo)
        return CreatePrinterController(use_case)

    def create_printer_controller(self) -> CreatePrinterController:
        return self.init_create_printer_controller()

    @lru_cache
    def init_list_printers_controller(self) -> ListPrintersController:
        use_case = ListPrintersUseCase(self._printer_repo)
        return ListPrintersController(use_case)

    def get_all_printers_controller(self) -> ListPrintersController:
        return self.init_list_printers_controller()

    @lru_cache
    def init_get_status_controller(self) -> GetStatusController:
        use_case = GetStatusUseCase(self._printer_discovery_service)
        return GetStatusController(use_case)

    def get_printer_status_controller(self) -> GetStatusController:
        return self.init_get_status_controller()

    @lru_cache
    def init_update_printer_controller(self) -> UpdatePrinterController:
        use_case = UpdatePrinterUseCase(self._printer_repo)
        return UpdatePrinterController(use_case)

    def update_printer_controller(self) -> UpdatePrinterController:
        return self.init_update_printer_controller()

    @lru_cache
    def init_delete_printer_controller(self) -> DeletePrinterController:
        use_case = DeletePrinterUseCase(self._printer_repo)
        return DeletePrinterController(use_case)

    def delete_printer_controller(self) -> DeletePrinterController:
        return self.init_delete_printer_controller()

    @lru_cache
    def init_discover_printer_controller(self) -> DiscoverPrinterController:
        use_case = DiscoverPrinterUseCase(self._printer_discovery_service)
        return DiscoverPrinterController(use_case)

    def discover_printer_controller(self) -> DiscoverPrinterController:
        return self.init_discover_printer_controller()

    @lru_cache
    def init_get_one_status_by_name_controller(self) -> GetOneStatusByNameController:
        use_case = GetOneStatusByNameUseCase(self._printer_discovery_service)
        return GetOneStatusByNameController(use_case)

    def get_one_status_by_name_controller(self, name: str = None) -> GetOneStatusByNameController:
        return self.init_get_one_status_by_name_controller()

    @lru_cache
    def init_print_test_page_controller(self) -> PrintTestPageController:
        use_case = PrintTestPageUseCase(
            self._printer_repo,
            self._channel_repo,
            self._template_repo,
            self._print_job_repo
        )
        return PrintTestPageController(use_case)

    def print_test_page_controller(self) -> PrintTestPageController:
        return self.init_print_test_page_controller()

    # --- Channel Controllers ---

    @lru_cache
    def init_list_channels_controller(self) -> ListChannelsController:
        use_case = ListChannelsUseCase(self._channel_repo, self._template_repo)
        return ListChannelsController(use_case)

    def get_all_channels_controller(self) -> ListChannelsController:
        return self.init_list_channels_controller()

    @lru_cache
    def init_create_channel_controller(self) -> CreateChannelController:
        use_case = CreateChannelUseCase(self._channel_repo)
        return CreateChannelController(use_case)

    def create_channel_controller(self) -> CreateChannelController:
        return self.init_create_channel_controller()

    @lru_cache
    def init_update_channel_controller(self) -> UpdateChannelController:
        use_case = UpdateChannelUseCase(self._channel_repo)
        return UpdateChannelController(use_case)

    def update_channel_controller(self) -> UpdateChannelController:
        return self.init_update_channel_controller()

    @lru_cache
    def init_delete_channel_controller(self) -> DeleteChannelController:
        use_case = DeleteChannelUseCase(self._channel_repo)
        return DeleteChannelController(use_case)

    def delete_channel_controller(self) -> DeleteChannelController:
        return self.init_delete_channel_controller()

    # --- Template Controllers ---

    @lru_cache
    def init_list_templates_controller(self) -> ListTemplatesController:
        use_case = ListTemplatesUseCase(self._template_repo)
        return ListTemplatesController(use_case)

    def get_all_templates_controller(self) -> ListTemplatesController:
        return self.init_list_templates_controller()

    @lru_cache
    def init_label_preview_controller(self) -> PreviewLabelController:
        use_case = PreviewLabelUseCase(
            template_service=self._label_template_service,
            channel_repo=self._channel_repo,
            template_repo=self._template_repo
        )
        return PreviewLabelController(use_case)

    def label_preview_controller(self) -> PreviewLabelController:
        return self.init_label_preview_controller()

    @lru_cache
    def init_remito_preview_controller(self) -> PreviewRemitoController:
        use_case = PreviewRemitoUseCase(
            template_service=self._remito_template_service,
            channel_repo=self._channel_repo,
            template_repo=self._template_repo
        )
        return PreviewRemitoController(use_case)

    def remito_preview_controller(self) -> PreviewRemitoController:
        return self.init_remito_preview_controller()

    # --- Print Job Controllers ---

    @lru_cache
    def init_list_print_jobs_controller(self) -> ListPrintJobsController:
        use_case = ListPrintJobsUseCase(self._print_job_repo)
        return ListPrintJobsController(use_case)

    def get_all_print_jobs_controller(self) -> ListPrintJobsController:
        return self.init_list_print_jobs_controller()

    @lru_cache
    def init_create_print_job_controller(self) -> CreatePrintJobController:
        use_case = CreatePrintJobUseCase(self._print_job_repo)
        return CreatePrintJobController(use_case)

    def create_print_job_controller(self) -> CreatePrintJobController:
        return self.init_create_print_job_controller()

    @lru_cache
    def init_print_job_controller(self) -> PrintJobController:
        use_case = PrintJobUseCase()
        return PrintJobController(use_case)

    def print_job_controller(self) -> PrintJobController:
        return self.init_print_job_controller()

container = Container()
