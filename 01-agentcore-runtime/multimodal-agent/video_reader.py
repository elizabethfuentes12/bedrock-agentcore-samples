from strands import tool
import boto3
import os
import base64
import cv2
import tempfile
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional

@tool
def video_reader(
    video_path: str, 
    text_prompt: str = "Describe what you see in this video",
    model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    region: Optional[str] = None,
    system_prompt: Optional[str] = None,
    agent = None
) -> Dict[str, Any]:
    """
    Analyze video content by extracting frames and analyzing them locally.
    
    This tool processes videos by extracting key frames and analyzing them
    using Claude models without requiring S3 upload.
    
    Args:
        video_path: Path to local video file
        text_prompt: Question or instruction for analyzing the video
        model_id: Bedrock model ID to use for analysis
        region: AWS region for Bedrock client
        system_prompt: Custom system prompt for analysis
        agent: The Strands agent instance (automatically provided by framework)
        
    Returns:
        Dictionary with video analysis results
    """
    try:
        # Get parameters from agent if not provided
        if not region and agent and hasattr(agent, 'model'):
            if hasattr(agent.model, 'boto_session') and agent.model.boto_session:
                region = agent.model.boto_session.region_name
            elif hasattr(agent.model, 'region'):
                region = agent.model.region
            else:
                region = "us-west-2"
        elif not region:
            region = "us-west-2"
            
        if not system_prompt and agent and hasattr(agent, 'system_prompt'):
            system_prompt = agent.system_prompt
        elif not system_prompt:
            system_prompt = "Always answer in the same language you are asked."
        
        # Check if video file exists
        if not os.path.exists(video_path):
            return {
                "status": "error",
                "content": [{"text": f"❌ Video file not found: {video_path}"}]
            }
        
        # Extract frames from video
        frames = _extract_video_frames(video_path)
        if not frames:
            return {
                "status": "error",
                "content": [{"text": "❌ Failed to extract frames from video"}]
            }
        
        # Initialize Bedrock client
        session = boto3.Session(region_name=region)
        bedrock_client = session.client('bedrock-runtime')
        
        # Analyze frames using Claude
        analysis_results = []
        for i, frame_data in enumerate(frames):
            message = {
                "role": "user",
                "content": [
                    {"text": f"Frame {i+1}: {text_prompt}"},
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {"bytes": frame_data}
                        }
                    }
                ]
            }
            
            response = bedrock_client.converse(
                modelId=model_id,
                messages=[message],
                system=[{"text": system_prompt}]
            )
            
            frame_analysis = response['output']['message']['content'][0]['text']
            analysis_results.append(f"**Frame {i+1}:** {frame_analysis}")
        
        # Combine all frame analyses
        combined_analysis = "\n\n".join(analysis_results)
        
        detailed_response = f"""🎥 Video Analysis Results:

{combined_analysis}

---
**Technical Details:**
- Model Used: {model_id}
- Region: {region}
- Video Path: {video_path}
- Frames Analyzed: {len(frames)}
"""
        
        return {
            "status": "success",
            "content": [{"text": detailed_response}]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"❌ Error processing video: {str(e)}"}]
        }


def _extract_video_frames(video_path: str, max_frames: int = 3) -> list:
    """Extract key frames from video using OpenCV."""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            return []
        
        # Calculate frame indices to extract (beginning, middle, end)
        frame_indices = []
        if max_frames == 1:
            frame_indices = [total_frames // 2]
        elif max_frames == 2:
            frame_indices = [0, total_frames - 1]
        else:
            step = total_frames // max_frames
            frame_indices = [i * step for i in range(max_frames)]
            if frame_indices[-1] >= total_frames:
                frame_indices[-1] = total_frames - 1
        
        frames = []
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                # Convert frame to JPEG bytes
                _, buffer = cv2.imencode('.jpg', frame)
                frames.append(buffer.tobytes())
        
        cap.release()
        return frames
        
    except Exception as e:
        print(f"Frame extraction error: {e}")
        return []