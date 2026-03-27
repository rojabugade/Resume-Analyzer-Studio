def run_resume_eval() -> dict[str, object]:
	from resume_analyzer.evals.harness import run_resume_eval as _run_resume_eval

	return _run_resume_eval()


__all__ = ["run_resume_eval"]
