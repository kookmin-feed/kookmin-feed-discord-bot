from config.logger_config import setup_logger
from config.db_config import get_database
from utils.scrapper_type import ScrapperType
from utils.scrapper_factory import ScrapperFactory
from config.db_config import save_notice

logger = setup_logger(__name__)


async def check_new_scrapper():
    """
    모든 스크래퍼 타입에 대해 컬렉션을 확인하고,
    컬렉션이 없거나 비어있는 경우 최신 공지사항으로 초기화합니다.
    """
    db = get_database()

    # 모든 스크래퍼 타입에 대해 검사
    for scrapper_type in ScrapperType.get_active_scrappers():
        collection_name = scrapper_type.get_collection_name()
        collection = db[collection_name]

        # 컬렉션이 비어있는지 확인
        if collection.count_documents({}) == 0:
            logger.info(f"비어있는 컬렉션 초기화 시작: {collection_name}")
            try:
                # 스크래퍼 생성
                scrapper = ScrapperFactory().create_scrapper(scrapper_type)
                if not scrapper:
                    logger.error(f"스크래퍼 생성 실패: {collection_name}")
                    continue

                # 최신 공지사항 가져오기
                notices = await scrapper.check_updates()

                # DB에 저장
                for notice in notices:
                    await save_notice(notice, scrapper_type)

                logger.info(
                    f"컬렉션 초기화 완료: {collection_name} ({len(notices)}개의 공지사항 저장)"
                )

            except Exception as e:
                logger.error(f"컬렉션 초기화 중 오류 발생 ({collection_name}): {e}")
                continue


async def run_check_new_scrapper():
    """초기화 프로세스를 실행합니다."""
    logger.info("=" * 65)
    logger.info("▶ 새로운 스크래퍼 확인 작업이 시작되었습니다.")
    logger.info("=" * 65)

    await check_new_scrapper()

    logger.info("=" * 65)
    logger.info("✅ 새로운 스크래퍼 확인 작업이 완료되었습니다.")
    logger.info("=" * 65)
