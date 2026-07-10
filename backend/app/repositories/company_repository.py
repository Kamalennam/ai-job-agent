from datetime import UTC, datetime

from app.models.company import Company


class CompanyRepository:
    @staticmethod
    async def get_by_slug(slug: str) -> Company | None:
        return await Company.find_one(Company.slug == slug)

    @staticmethod
    async def list_enabled_greenhouse() -> list[Company]:
        return await Company.find(
            Company.enabled == True,  # noqa: E712
            Company.ats_type == "greenhouse",
        ).to_list()

    @staticmethod
    async def upsert_from_board(slug: str, name: str, careers_url: str | None) -> Company:
        existing = await CompanyRepository.get_by_slug(slug)
        if existing:
            existing.name = name
            existing.careers_url = careers_url or existing.careers_url
            existing.enabled = True
            await existing.save()
            return existing

        company = Company(
            name=name,
            slug=slug,
            ats_type="greenhouse",
            careers_url=careers_url or f"https://boards.greenhouse.io/{slug}",
            enabled=True,
        )
        return await company.insert()

    @staticmethod
    async def mark_collected(company: Company) -> None:
        company.last_collected_at = datetime.now(UTC)
        await company.save()
