import json

class JudgmentExplainer:
    """
    Synthesizes multiple reasoning signals into a cohesive legal narrative.
    Inspired by NyayaRAG's explanation task.
    """
    
    def generate(self, result_dict):
        """
        Takes the output of run_inference and builds a structured explanation.
        """
        jp = result_dict.get("judgment_probability", {})
        prediction = jp.get("prediction", "Unknown")
        confidence = jp.get("confidence", 0.0)
        reasoning = jp.get("reasoning", {})
        
        # 1. Base Logic
        narrative = [
            f"The system predicts that this case result is '{prediction}' with a confidence coefficient of {confidence:.4f}.",
            f"Logic: Combined weighted synthesis of Feature Probability ({reasoning.get('base_probability', 0.5):.2f}), "
            f"Symbolic Alignment ({reasoning.get('symbolic_alignment', 0.5):.2f}), and "
            f"Precedent Consistency."
        ]
        
        # 2. KG Grounding
        concepts = reasoning.get("detected_concepts", [])
        if concepts:
            narrative.append(
                f"Knowledge Grounding: Detected high-level concepts: {', '.join(concepts)}. "
                f"Statutory logic applied: {', '.join(reasoning.get('legal_logic', []))}."
            )

        # 3. Discriminative Alignment (Precedent verification)
        pc = reasoning.get("precedent_consistency", {})
        if pc:
            cons_allowed = pc.get("allowed", 0.0)
            if cons_allowed > 0.6:
                narrative.append(
                    f"Structural Alignment: This case shows high feature-level consistency with successful historical clusters."
                )
            elif cons_allowed < 0.3:
                narrative.append(
                    f"Reasoning Tension: Feature patterns show structural similarity to dismissed precedents, creating a risk threshold."
                )
                
        # 4. Evidentiary "Lift" (Counterfactuals)
        cf = jp.get("counterfactuals", {})
        if cf and isinstance(cf, dict):
            # Find the best lift
            valid_cf = {k: v for k, v in cf.items() if isinstance(v, dict) and "delta" in v}
            if valid_cf:
                best_f = max(valid_cf.items(), key=lambda x: x[1]["delta"])
                feat_name = best_f[0].replace("ev_", "").replace("fg_", "").replace("_", " ").title()
                lift = best_f[1].get("lift_percent", 0.0)
                narrative.append(
                    f"Counterfactual Pivot: Analysis identifies '{feat_name}' as the primary evidentiary gap. "
                    f"Its inclusion is projected to increase victory probability by +{lift}%."
                )
            
        return {
            "summary_narrative": " ".join(narrative),
            "logical_steps": narrative,
            "fidelity_score": confidence
        }
