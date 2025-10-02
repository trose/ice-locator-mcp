import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  UpdateContinuousDeploymentPolicyRequest,
  UpdateContinuousDeploymentPolicyResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateContinuousDeploymentPolicyCommandInput
  extends UpdateContinuousDeploymentPolicyRequest {}
export interface UpdateContinuousDeploymentPolicyCommandOutput
  extends UpdateContinuousDeploymentPolicyResult,
    __MetadataBearer {}
export declare class UpdateContinuousDeploymentPolicyCommand extends $Command<
  UpdateContinuousDeploymentPolicyCommandInput,
  UpdateContinuousDeploymentPolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateContinuousDeploymentPolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateContinuousDeploymentPolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    UpdateContinuousDeploymentPolicyCommandInput,
    UpdateContinuousDeploymentPolicyCommandOutput
  >;
  private serialize;
  private deserialize;
}
